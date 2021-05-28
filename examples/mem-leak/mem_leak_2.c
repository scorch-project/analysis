#define SIZE 12
int main()
{
    union {
        int *p0;
        struct {
            char p1[SIZE];
            int p2;
        } str;
    } data;
    data.p0 = (int*) malloc(sizeof(int*));
	for(int i = 0; i < SIZE; i++)
	{
		data.str.p1[i] = 0;
	}
    data.str.p2 = 0;
    free(data.p0);
	return 0;
}
