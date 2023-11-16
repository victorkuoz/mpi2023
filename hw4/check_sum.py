from gpio import LightSender

def checkSum(encode):

    binary_sum = sum(int(e, 2) for e in encode)
    # print(binary_sum)
    binary_sum = format(binary_sum, 'b')
    print(binary_sum)

    # Adding the overflow bits
    if(len(binary_sum) > 8):
        binary_sum = binary_sum[-8:]
    #    binary_sum = format(int(binary_sum[0:x], 2) + int(binary_sum[x:], 2), 'b')

    if(len(binary_sum) < 8):
        binary_sum = '0' * (8 - len(binary_sum)) + binary_sum
    
    print(binary_sum)

    return binary_sum 

def main():
    sender = LightSender(st=1.0)
    msg = "hello checksum"
    encode_msg = sender.encode(msg)
    print(encode_msg)
    # encode_msg = ['10101011011']
    ret = checkSum(encode_msg)
    print(ret)

    recv = checkSum(encode_msg)
    print(recv)

if __name__ == "__main__":
    main()