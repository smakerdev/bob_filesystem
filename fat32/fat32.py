import sys


def read_sectors(fd, sector, count=1):
    fd.seek(sector * 512)
    return fd.read(count * 512)


def l2b(data):
    return int(("0x" + data[::-1].hex()), 16)


def bps(data):
    return l2b(data[11:13])


def root_dir_sector(data):
    return (l2b(data[17:19]) * 32 + (bps(data) - 1)) / bps(data)


def first_data_sector(data):
    return int(l2b(data[14:16]) + l2b(data[36:40]) * l2b(data[16:17]) + root_dir_sector(data))


def cluster_to_sector(cluster, data):
    return (cluster - 2) * l2b(data[13:14]) + first_data_sector(data)


name = ['', '', '', '', '', '', '', '', '']
idx = 0


def get_info(data):
    global idx
    global name

    if (len(data) <= 0):
        return 0

    if (l2b(data[11:12]) == 0x08):

        if (l2b(data[0:1]) == 0xe5):

            print("deleted ", end='')

        else:
            name1 = data[0:11]
            print("Volumn :", name1.decode('euc-kr'))

    if (l2b(data[11:12]) == 0x0f):
        n = ""
        name1 = data[1:11].decode('utf-16').split(b'\x00\x00'.decode('utf-16'))[0]
        name2 = data[14:26].decode('utf-16').split(b'\x00\x00'.decode('utf-16'))[0]
        name3 = data[28:32].decode('utf-16').split(b'\x00\x00'.decode('utf-16'))[0]

        name[idx] = (name1 + name2 + name3).split(b'\xff\xff'.decode('utf-16'))[0]
        idx += 1

        if (l2b(data[43:44]) != 0x0f):
            if (l2b(data[0:1]) == 0xe5):
                print("deleted ", end='')
            print(end='')
            while (idx >= 0):
                n += name[idx]
                idx -= 1
            print(n)
            name = ['', '', '', '', '', '', '', '', '']
            idx = 0

    if (l2b(data[11:12]) == 0x16):

        if (l2b(data[0:1]) == 0xe5):
            print("deleted ", end='')

        name1 = data[0:11].decode('euc-kr')
        print(name1)

    if (l2b(data[11:12]) == 0x10):

        if (l2b(data[0:1]) == 0xe5):
            print("deleted ", end='')

        name1 = data[0:8].decode('euc-kr')
        print(name1)

    if (l2b(data[11:12]) == 0x20):

        if (l2b(data[0:1]) == 0xe5):
            name1 = "!" + data[1:8].decode('euc-kr')
            print("deleted ", end='')

        else:
            name1 = data[0:8].decode('euc-kr')

        if (data[8:9] != b'\x20'):
            name1 += "." + data[8:11].decode('euc-kr')
        print(name1)

    get_info(data[32:])


if __name__ == "__main__":
    filename = sys.argv[1]
    f = open(filename, 'rb')

    data = read_sectors(f, cluster_to_sector(2, read_sectors(f, 0)), 1)
    get_info(data)

    f.close()
