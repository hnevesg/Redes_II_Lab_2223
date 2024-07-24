
import sys
import struct

if __name__ == "__main__": 

  filepath = sys.argv[1]

  FORMAT = ">BBIIH"

  with open(filepath,"r") as unpacked_file:
    content = unpacked_file.readlines()
    with open("text","w") as file:
      for line in content:
        hour,minute,phone1,phone2,duration = line.split(';')
        header = struct.pack(FORMAT, int(hour), int(minute), int(phone1), int(phone2), int(duration))  
        print(bytes(header))
        file.write(str(header))
        file.write('\n')

  sys.exit(0)