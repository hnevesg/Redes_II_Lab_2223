#!/usr/bin/env python3

import struct
import sys

FORMAT = ">BBIIH"
def unpack_line(line:bytes) -> tuple:
    return struct.unpack(FORMAT,line)

#public main 
if __name__ == "__main__": #solo cuando se este ejecutando
    filepath = sys.argv[1]

    with open(filepath,"rb") as packed_file: #b=binario
        content = packed_file.read()

    registry_size = struct.calcsize(FORMAT) #12 bits

    index=0
    end = index + registry_size

    while True:
        registry = content[index:end]
        if not registry: # si está vacío
            break
        index = end
        end += registry_size

        hour, minute,caller,receiver,duration=unpack_line(registry)

        print(f"Call from {caller} to {receiver} at {hour}:{minute} for {duration} minutes")

    sys.exit(0)

# hora y numeros no pueden ser negativos --> sin signo
