#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

#define NB_VL 4
#define NB_Q 8

// Headers
typedef bit<24>    MacAddr_t;   
typedef bit<16>    VLid_t;     

typedef bit<32> ip4Addr_t;
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
//int
#define MAX_INT_HEADERS 5 
const bit<5>  IPV4_OPTION_INT = 31;//option
//int header
typedef bit<13> switch_id_t;
typedef bit<13> queue_depth_t;
typedef bit<6>  output_port_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>     etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<6>    dscp;
    bit<2>    tos;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}
//option int header
header ipv4_option_t {
    bit<1> copyFlag;
    bit<2> optClass;
    bit<5> option;
    bit<8> optionLength;
}

header int_count_t {
    bit<16>   num_switches;
}

header int_header_t {
    bit<32> qdepth;
    bit<32> lambda1;
    bit<32> lambda2;
    //bit<32> swid;
    //bit<32> qdepth;
    //bit<32> lambda1;
}


struct parser_metadata_t {
    bit<16> num_headers_remaining;
}

struct metadata {
    bit<16> curr_usage;
    bit<16> below_usage;
    bit<16>      dstVL;
    parser_metadata_t  parser_metadata;
    bit<32> num;
    bit<32> omega;

}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    //int
    ipv4_option_t ipv4_option;
    int_count_t   int_count;
    int_header_t[MAX_INT_HEADERS] int_headers;
}

error { IPHeaderWithoutOptions }

// Parser
parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }


    state parse_ipv4 {
        packet.extract(hdr.ipv4);

        verify(hdr.ipv4.ihl >= 5, error.IPHeaderWithoutOptions);
        transition select(hdr.ipv4.ihl) {
            5             : accept;
            default       : parse_ipv4_option;
        }
    }

    state parse_ipv4_option {
        packet.extract(hdr.ipv4_option);
        transition select(hdr.ipv4_option.option){
            IPV4_OPTION_INT:  parse_int;
            default: accept;
        }
    }

    state parse_int {
        packet.extract(hdr.int_count);
        meta.parser_metadata.num_headers_remaining = hdr.int_count.num_switches;
        transition select(meta.parser_metadata.num_headers_remaining){
            0: accept;
            default: parse_int_headers;
        }
    }

    state parse_int_headers {
        packet.extract(hdr.int_headers.next);
        meta.parser_metadata.num_headers_remaining = meta.parser_metadata.num_headers_remaining -1 ;
        transition select(meta.parser_metadata.num_headers_remaining){
            0: accept;
            default: parse_int_headers;
        }
    }


}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

register<bit<16>>(NB_Q * NB_VL) usage;
register<bit<32>>(7*4) my_register;//W(1)\qepth(2)\omega(3)\K(4)\lambda1(5)\lambda2(6)

// Controls
control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action Drop() {
        mark_to_drop(standard_metadata);
    }


    action Check_VL(bit<16> dst_vl, bit<32> omega) {
        meta.omega = omega;
        meta.dstVL = dst_vl;
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        
        hdr.ethernet.dstAddr = dstAddr;
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl -1;

    }

    table vl_table {
        key = {
            hdr.ethernet.srcAddr : exact;
        }
        actions = {
            Check_VL;
            //Drop;
            NoAction;
        }
        default_action = NoAction();
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            //Drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {       
        if (hdr.ipv4.isValid()){
            ipv4_lpm.apply();
            vl_table.apply();

            //Record the length of the current virtual queue q
            bit<32> num;
            my_register.read(num,(bit<32>)meta.dstVL*7+2);
            my_register.write((bit<32>)meta.dstVL*7+2,num+1);


            //wrr
            #include "wrr765.p4"
        }
    }
}

// Egress
control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action mark_ecn() {
        hdr.ipv4.tos = 3;
    }

    action add_int_header(bit<32> swid){
        //increase int stack counter by one
        hdr.int_count.num_switches = hdr.int_count.num_switches + 1;
        hdr.int_headers.push_front(1);
        // This was not needed in older specs. Now by default pushed
        // invalid elements are
        hdr.int_headers[0].setValid();
        hdr.int_headers[0].qdepth = (bit<32>)standard_metadata.deq_qdepth;
        my_register.read(hdr.int_headers[0].lambda1,(bit<32>)meta.dstVL*7+5);
        my_register.read(hdr.int_headers[0].lambda2,(bit<32>)meta.dstVL*7+6);
        //update ip header length
        hdr.ipv4.ihl = hdr.ipv4.ihl + 3;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 12;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 12;
    }


    table int_table {
        actions = {
            add_int_header;
            NoAction;
        }
        default_action = NoAction();
    }
    
    
    apply {

        if (hdr.ipv4.isValid() && standard_metadata.instance_type == 0 ){
            //wrr
            //Update curr_usage to read the number of current priorities present for the current type
            usage.read(meta.curr_usage, (bit<32>)(standard_metadata.priority) + (bit<32>)(NB_Q*meta.dstVL));
            //Lowest priority
            if (5 == standard_metadata.priority){
                //Set it to 0 so that it is treated as "tail" in the next "if"
                meta.below_usage = 0;
            }else{
                //If this is any other queue except the last one, then it has a "below" and below_usage represents the next priority queue capacity, i.e. the number of reads that exist at the next priority of the current type
                usage.read(meta.below_usage, (bit<32>)(standard_metadata.priority)-1 + (bit<32>)(NB_Q*meta.dstVL));
            }

            if (0 == meta.below_usage){//In this case, the capacity of the next priority queue of VL is 0, so it is the last queue
                if (0 == meta.curr_usage-1){//There is only one packet in the queue
                    usage.write((bit<32>)(0 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(1 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(2 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(3 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(4 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(5 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(6 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(7 + NB_Q*meta.dstVL), 0);
                }else{//At this time, the current VL has multiple priority packets, forwards the packets, and updates meta.curr_usage
                    usage.write((bit<32>)(standard_metadata.priority) + (bit<32>)(NB_Q*meta.dstVL), meta.curr_usage-1);
                }
            } 


            if (hdr.int_count.isValid() &&  hdr.ipv4.tos==1){
                int_table.apply();
            }


            //clone
            if(hdr.ipv4.tos==1 && standard_metadata.deq_qdepth >= 11 ){
                if(standard_metadata.ingress_port == 1){
                    clone(CloneType.E2E,101);
                }else if(standard_metadata.ingress_port == 2){
                    clone(CloneType.E2E,102);
                }else if(standard_metadata.ingress_port == 3){
                    clone(CloneType.E2E,103);
                }
            }

        }


        if(standard_metadata.instance_type == 2 ){
            macAddr_t temp;
            ip4Addr_t temp_ip;
            mark_ecn();//ecn               
            //mac
            temp = hdr.ethernet.srcAddr;
            hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
            hdr.ethernet.dstAddr = temp;
            //ip
            temp_ip = hdr.ipv4.srcAddr;
            hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
            hdr.ipv4.dstAddr = temp_ip;
        }              
    }
}

// XXX
control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.tos,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

// Deparser
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        //packet.emit(hdr.udp);
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.int_count);
        packet.emit(hdr.int_headers);
    }
}


// Execution
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
