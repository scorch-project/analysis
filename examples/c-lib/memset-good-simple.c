//#include <string.h>
#define LEN 1
extern void *memset(void*, int, unsigned long);
int main()
{
	char buffer[LEN];
  	memset(buffer, 0, LEN);
  	return 0;
}
