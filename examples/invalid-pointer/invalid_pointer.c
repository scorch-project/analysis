#include <stdlib.h>
int main()
{
	int *i;
	i = (int *)malloc(sizeof(int));
	free(i);
	*i = 15;
	return 0;
}
