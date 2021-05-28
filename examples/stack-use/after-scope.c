int main()
{
    int *ptr;
	{
		int var = 0;
		ptr = &var;
	}
	*ptr = 1;
	return 0;
}
