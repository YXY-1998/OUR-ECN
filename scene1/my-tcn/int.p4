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
#define MAX_INT_HEADERS 5 //最大int包头数量
const bit<5>  IPV4_OPTION_INT = 31;//option匹配项
//int header单位
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
    bit<4>    ihl;//首部长度，包括选项字段，单位32bit,ihl=5时，表示IP包长度为20bytes
    bit<6>    dscp;
    bit<2>    tos;
    bit<16>   totalLen;//总长度，IP数据报的最大长度为1500bytes。常规的无选项的IP包头长度为20bytes
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
//int头计数器
header int_count_t {
    bit<16>   num_switches;
}
//int头
header int_header_t {
    bit<32> qdepth;//队列深度,以数据包数量为单位bit<13>
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
    bit<16> curr_usage;//同一vl中到达的数据包数
    bit<16> below_usage;//剩余可用空间？
    bit<16>      dstVL;//目标虚拟队列号
    parser_metadata_t  parser_metadata;
    bit<32> num;//到达数据包数lambda
    bit<32> omega;

}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    //int头
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

    //int解析
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        //检查ihl是否大于5。没有ip选项的数据包将ihl设置为5。在没有选项时，该字段的值为5
        verify(hdr.ipv4.ihl >= 5, error.IPHeaderWithoutOptions);
        transition select(hdr.ipv4.ihl) {
            5             : accept;//ihl=5时，接受
            default       : parse_ipv4_option;//ihl>5时，说明有option和int头
        }
    }

    state parse_ipv4_option {
        packet.extract(hdr.ipv4_option);
        transition select(hdr.ipv4_option.option){
            IPV4_OPTION_INT:  parse_int;//hdr.ipv4_option.option=31时
            default: accept;
        }
    }

    state parse_int {
        packet.extract(hdr.int_count);
        meta.parser_metadata.num_headers_remaining = hdr.int_count.num_switches;
    //    meta.num_headers_remaining = hdr.int_count.num_switches;
    //    transition select(meta.num_headers_remaining){
        transition select(meta.parser_metadata.num_headers_remaining){
            0: accept;//当前int头数量为0，路过交换机数量为0
            default: parse_int_headers;
        }
    }

    state parse_int_headers {
        packet.extract(hdr.int_headers.next);//循环解析int头，直到全部解析完成
        meta.parser_metadata.num_headers_remaining = meta.parser_metadata.num_headers_remaining -1 ;
        //meta.num_headers_remaining = meta.num_headers_remaining -1 ;
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
register<bit<32>>(7*4) my_register;//记录W(1)\qepth(2)\omega(3)\K(4)\lambda1(5)\lambda2(6)

// Controls
control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action Drop() {
        mark_to_drop(standard_metadata);
    }

    ///确定虚拟队列
    action Check_VL(bit<16> dst_vl, bit<32> omega) {
        meta.omega = omega;
        meta.dstVL = dst_vl;
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        
        hdr.ethernet.dstAddr = dstAddr;
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl -1;

    }

    //根据源ethernet地址分类
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
            ipv4_lpm.apply();//路由
            //根据ip分类
            vl_table.apply();

            //wrr7_6_5();轮询优先级分配
            #include "wrr765.p4"
        }
    }//end_spply
}

// Egress
control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action mark_ecn() {
        hdr.ipv4.tos = 3;
    }
    //添加int头
    action add_int_header(bit<32> swid){
        //increase int stack counter by one将int堆栈计数器加1
        hdr.int_count.num_switches = hdr.int_count.num_switches + 1;
        hdr.int_headers.push_front(1);
        // This was not needed in older specs. Now by default pushed这在旧的规格中是不需要的。默认是push
        // invalid elements are无效元素为
        hdr.int_headers[0].setValid();
        //hdr.int_headers[0].swid = (bit<32>)swid;
        hdr.int_headers[0].qdepth = (bit<32>)standard_metadata.deq_qdepth;
        //hdr.int_headers[0].lambda1 = (bit<32>)standard_metadata.priority;
        my_register.read(hdr.int_headers[0].lambda1,(bit<32>)meta.dstVL*7+5);
        my_register.read(hdr.int_headers[0].lambda2,(bit<32>)meta.dstVL*7+6);
        //update ip header length更新IP头长度
        hdr.ipv4.ihl = hdr.ipv4.ihl + 3;//1的单位为32bit,相当于一个int长度
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 12;//单位Byte
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


            //wrr队列计数器更新
            //更新curr_usage,读取当前类型当前优先级存在的数量
            usage.read(meta.curr_usage, (bit<32>)(standard_metadata.priority) + (bit<32>)(NB_Q*meta.dstVL));
            //最低优先级
            //if (0 == standard_metadata.priority)
            if (5 == standard_metadata.priority){
                //将其设为0，以便在下一个“if”中被视为“tail”`
                meta.below_usage = 0;
            }else{
                //如果这是除最后一个队列之外的任何其他队列，则它有一个“below”，below_usage表示下一个优先级队列容量，即读取当前类型下一优先级存在的数量
                usage.read(meta.below_usage, (bit<32>)(standard_metadata.priority)-1 + (bit<32>)(NB_Q*meta.dstVL));
            }
            //如果是尾部，则此队列中的空闲1
            if (0 == meta.below_usage){//此时VL的下一个优先级队列的容量为0，所以为最后一个队列
                if (0 == meta.curr_usage-1){//此时队列中只有一个数据包
                    usage.write((bit<32>)(0 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(1 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(2 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(3 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(4 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(5 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(6 + NB_Q*meta.dstVL), 0);
                    usage.write((bit<32>)(7 + NB_Q*meta.dstVL), 0);
                }else{//此时当前VL有多个优先级数据包，转发数据包，更新meta.curr_usage
                    usage.write((bit<32>)(standard_metadata.priority) + (bit<32>)(NB_Q*meta.dstVL), meta.curr_usage-1);
                }
            } 
            ///wrr结束


            //判断是否增加INT字段，tos=1且type=0增加
            if (hdr.int_count.isValid()){
                int_table.apply();
            }

            //读取ecn标记t
            bit<32> t;
            my_register.read(t,(bit<32>)11);//初始化t=my_register[11]

            log_msg("vl = {}, q = {}, qdepth = {}",{meta.dstVL, meta.num, standard_metadata.deq_qdepth});
            //clone
            //if(standard_metadata.instance_type == 0 && standard_metadata.deq_qdepth >= (bit<19>)k){//>11标记
            if(t!=0 && standard_metadata.deq_timedelta >= t ){//>11标记
                mark_ecn();//标记ecn  
            }//end_ecn

        }//end_type=0
      
        
    }//end_apply
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
        packet.emit(hdr.int_headers);//新加的int包头
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
