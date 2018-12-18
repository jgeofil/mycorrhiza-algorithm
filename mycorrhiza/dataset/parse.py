with open("/home/jeremy/Desktop/ALBgbs_Native_imputed.str") as fin:
    with open("/home/jeremy/Desktop/ALBgbs_Native_imputed_sup.str", "w+") as fout:
        for line in fin.readlines():
            line = line.strip().split()
            if line[1] in ['KNA','EBCL','YUNNAN','ULS']:
                line[2] = "0"
                print("yes")
            else: line[2] = "1"
            fout.write("\t".join(line)+"\n")