#ENAMDICT entry sample:
# さより /(f) Sayori/
# さよ子 [さよこ] /(f) Sayoko/

output = open("enamdict.sql", "w", encoding="utf8")
output.write("create table if not exists enamdict (name, contents);\n")
output.write("begin transaction;\n")

with open("enamdict.utf", "r", encoding="utf8") as f:
    for line in f.readlines():
        line = line.strip()
        name = line[0:line.find("/")]
        secondaryReadingStart = name.find("[")
        secondaryReadingEnd = name.find("]")
        if secondaryReadingStart == -1: # there's only one reading
            # self.__addWordToDictionaryJ2E(name.strip(), line)
            output.write("insert into enamdict (name, contents) values ('{0}', '{1}');\n".format(name.strip().replace("'", "''"), line.replace("'", "''")))
        else:
            # self.__addWordToDictionaryJ2E(name[0:secondaryReadingStart].strip(), line)
            output.write("insert into enamdict (name, contents) values ('{0}', '{1}');\n".format(name[0:secondaryReadingStart].strip().replace("'", "''"), line.replace("'", "''")))
            # self.__addWordToDictionaryJ2E(name[secondaryReadingStart+1:secondaryReadingEnd].strip(), line)
            output.write("insert into enamdict (name, contents) values ('{0}', '{1}');\n".format(name[secondaryReadingStart+1:secondaryReadingEnd].strip().replace("'", "''"), line.replace("'", "''")))

output.write("end transaction;\n")
output.write("create index if not exists enamdict_name on enamdict (name);\n")
output.close()