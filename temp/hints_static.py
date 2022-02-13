import json

filename = 'ASL Browser notes.txt'


with open(filename) as file, open('dump.json', 'w') as json_file:
    items = []
    for line in file:
        if not line.strip():
            continue
        d = {}
        data = line.split('|')
        for val in data:
            key, sep, value = val.partition(':')
            d[key.strip()] = value.strip()
        items.append(d)
    json.dump(items, json_file)

print(items)

# fields = ['video', 'term', 'hint']
# with open(filename) as fh:
#     # count variable for employee id creation
#     l = 1
      
#     for line in fh:
#         description = list( line.strip().split(None, 3))
          
#         # for output see below
#         print(description) 

#         # for automatic creation of id for each term
#         sno ='emp'+str(l)
      
#         # loop variable
#         i = 0
    
#         # intermediate dictionary
#         dict2 = {}

#         while i<len(fields):
              
#             # creating dictionary for each term
#             dict2[fields[i]]= description[i]
#             i = i + 1
                  
#         # appending the record of each term to
#         # the main dictionary
#         dict1[sno]= dict2
#         l = l + 1
  
  
# # creating json file        
# out_file = open("test2.json", "w")
# json.dump(dict1, out_file, indent = 4)
# out_file.close()
