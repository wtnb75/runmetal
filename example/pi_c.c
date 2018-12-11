// gcc pi_c.c -o pi_c
// ./pi_c
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <math.h>
#include <unistd.h>

float randgen(){
  return (float)(random())/RAND_MAX;
}

unsigned long long gettime(){
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return (unsigned long long)(tv.tv_sec)*1000000ULL+tv.tv_usec;
}

int main(int argc, char **argv){
  int n=100000000;
  int ch;
  while((ch=getopt(argc, argv, "n:"))!=-1){
    switch(ch){
    case 'n':
      n=strtol(optarg, NULL, 0);
      break;
    }
  }
  int c=0;
  unsigned long long st;

  st=gettime();
  for(int i=0; i<n; i++){
    float x=randgen();
    float y=randgen();
    if(sqrt(x*x+y*y)<1.0){
      c++;
    }
  }
  unsigned long long en=gettime()-st;
  printf("pi: %d/%d*4=%f, %lld usec\n", c, n, (float)(c)/n*4.0, en);
  return 0;
}
