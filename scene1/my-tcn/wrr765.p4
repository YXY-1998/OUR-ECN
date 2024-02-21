#ifndef q
#else
#undef q
#endif

#undef q
#define q 7
usage.read(meta.curr_usage, (bit<32>)(q + NB_Q*meta.dstVL));//curr_usage=当前dstVL类型中q优先级数量
if (meta.curr_usage <= (bit<16>)meta.omega) {                                  
    usage.write((bit<32>)(q + NB_Q*meta.dstVL), meta.curr_usage+1); //当前dstVL类型中q优先级数量curr_usage+1
    standard_metadata.priority = q; //优先级为q                                     
} else {//如果当前dstVL类型中q优先级数量>权重 ,则将当前dstVL类型优先级降低
    #undef q
    #define q 6
    usage.read(meta.curr_usage, (bit<32>)(q + NB_Q*meta.dstVL));//curr_usage=当前dstVL类型中q优先级数量
    if (meta.curr_usage <= (bit<16>)meta.omega) {                                  
        usage.write((bit<32>)(q + NB_Q*meta.dstVL), meta.curr_usage+1);  
        standard_metadata.priority = q;                                      
    } else {
        #undef q
        #define q 5
        usage.read(meta.curr_usage, (bit<32>)(q + NB_Q*meta.dstVL));         
        if (meta.curr_usage <= (bit<16>)meta.omega) {                                 
            usage.write((bit<32>)(q + NB_Q*meta.dstVL), meta.curr_usage+1);  
            standard_metadata.priority = q;                                      
        } else {
            usage.write((bit<32>)(q + NB_Q*meta.dstVL), meta.curr_usage+1);  
            standard_metadata.priority = q;
        }//end5
    }//end6
}//end7
