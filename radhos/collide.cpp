#include <iostream>
#include <cstring>
#include <string>
#include <sstream>
using namespace std;

struct _Py_HashSecret_t {
  long long prefix;
  long long suffix;
} secret;

long long string_hash(const char *s, int len) {
  int sz = len;
  if (len == 0)
    return 0;
  long long x = secret.prefix;
  unsigned char *p = (unsigned char*)s;
  x ^= *p << 7;
  while (--sz >= 0)
    x = (1000003*x) ^ *p++;
  x ^= len;
  x ^= secret.suffix;
  if (x == -1)
    x = -2;
  return x;
}

int main(int argc, char **argv) {
  if (argc < 4) {
    cerr << "Usage: " << argv[0] << " string prefix suffix" << endl;
    return 1;
  }
  const char *s = argv[1];
  unsigned long long pref, suf;
  stringstream ss(argv[2]);
  ss >> pref;
  stringstream ss2(argv[3]);
  ss2 >> suf;
  secret.prefix = pref;
  secret.suffix = suf;
  cerr << "prefix = "<< secret.prefix << endl;
  cerr << "suffix = " << secret.suffix << endl;
  long long hash = string_hash(s, strlen(s)) & 0xffffffff;
  cerr << "hash = " << hash << endl;
  long long cnt = 0;
  int len = strlen(s);
  unsigned char *buf = (unsigned char*)alloca(len);
  memcpy(buf, s, len);
  int a = argc > 4 ? atoi(argv[4]) : 0;
  int b = argc > 5 ? atoi(argv[5]) : 256;
  cerr << "Scanning range " << a << " to " << b << endl;
  for (int first = a; first < b; ++first) {
    buf[0] = first;
    do {
    do {
    do {
    do {

    cnt++;
    unsigned int h = string_hash((char*)buf, len) & 0xffffffff;
    if (cnt % 100000000 == 0)
      cerr << "Progress: " << cnt << " " << h << endl;
    if (h == hash) {
      if (memcmp(buf, s, len)) {
        printf("\"");
        for (int i = 0; i < len; ++i) {
          printf("\\x%02x", buf[i]);
        }
        printf("\"\n");
        return 0;
      }
    }

    buf[4]++; } while (buf[4]);
    buf[3]++; } while (buf[3]);
    buf[2]++; } while (buf[2]);
    buf[1]++; } while (buf[1]);
  }
}
