from ast import literal_eval

ciphertext = int(open("ciphertext.txt").read())
pubkey = literal_eval(open("pubkey.txt").read())

def mat(pubkey, ciphertext):
    n = len(pubkey)
    A = Matrix(ZZ,n+1,n+1)
    for i in range(n):
        A[i,i] = 1
    for i in range(n):
        A[i,n] = pubkey[i]
    A[n,n] = -ciphertext
    return A

A = mat(pubkey, ciphertext)
print "Computing LLL..."
res = A.LLL()
sol = res[-3]
offset = 1
bits = [int(bool(x)) for x in sol][::-1][offset:]
res = ""
for i in range(0, len(bits), 8):
    b = "01" + "".join(map(str, bits[i+2:i+8]))
    res += chr(int(b,2))
print "Flag:", res
