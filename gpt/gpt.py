import sys
import struct

def read_sector(fd, sector, count = 1):
    fd.seek(sector * 512)
    return fd.read(count * 512)

filename = sys.argv[1]

f = open(filename, "rb")

data = read_sector(f, 0)

if data[-2] != 0x55 and data[-1] != 0xAA:
    print("no boot partition")

partition_header = data[446:446 + 64]

gpt_start = struct.unpack_from("<I", partition_header, 8)[0]

gpt_header = read_sector(f, gpt_start)

if struct.unpack_from("<8s", gpt_header, 0)[0]!= b'EFI PART' :
    print("no gpt")

part_entry_start = struct.unpack_from("<Q", gpt_header, 72)[0]
PartEntry_count = struct.unpack_from("<I", gpt_header, 80)[0]

partition_list = []
for idx in range(PartEntry_count):
    part_entry = read_sector(f, part_entry_start + idx)
    for entry_idx in range(4):
        entry = part_entry[entry_idx * 128:(entry_idx + 1) * 128]
        entry_start = struct.unpack_from("<Q", entry, 32)[0]
        entry_last = struct.unpack_from("<Q", entry, 40)[0]

        flag = False
        if entry_start == 0:
            flag = True
            break
        partition_list.append([entry_start, entry_last - entry_start+1])
        partition_list[-1] = [i*512 for i in partition_list[-1]]
    if flag:
        break
for i in range(len(partition_list)):
    print("Partition" + str(i+1) + "    StartAt:" + str(partition_list[i][0]) + "      Size:" + str(partition_list[i][1]))