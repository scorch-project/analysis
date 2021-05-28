#define LEN 1

struct my_type
{
	int array[LEN];
	int num;
}var;

int main()
{
	var.array[LEN] = 0;
	return 0;
}
