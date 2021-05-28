#include<stdbool.h>
#include<stdlib.h>

// #include<time.h>

// static bool initialised = 0;

// void initialise_rand()
// {
// 	if(!initialised)
// 		srand(time(NULL));
// }


int __VERIFIER_nondet_int()
{
	int i;
	return i;
}

char __VERIFIER_nondet_char()
{
	char i;
	return i;
}

bool __VERIFIER_nondet_bool()
{
	bool i;
	return i;
}

long __VERIFIER_nondet_long()
{
	long i;
	return i;
}

unsigned long __VERIFIER_nondet_ulong()
{
	unsigned long i;
	return i;
}

unsigned long long __VERIFIER_nondet_ulonglong()
{
	unsigned long i;
	return i;
}


unsigned int __VERIFIER_nondet_uint()
{
	unsigned int i;
	return i;
}


unsigned short __VERIFIER_nondet_ushort()
{
	unsigned short i;
	return i;
}

unsigned char __VERIFIER_nondet_uchar()
{
	unsigned char i;
	return i;
}

unsigned __VERIFIER_nondet_unsigned() 
{ 
	unsigned i;
	return i; 
}

size_t __VERIFIER_nondet_size_t() 
{ 
	size_t i;
	return i; 
}

// loff_t __VERIFIER_nondet_loff_t() 
// {
// 	loff_t i;
// 	return i; 
// }

// sector_t __VERIFIER_nondet_sector_t() 
// { 
// 	sector_t i;
// 	return i; 
// }

char* __VERIFIER_nondet_pchar() 
{
	char *i; 
	return i; 
}

short __VERIFIER_nondet_short() 
{
	short i; 
	return i; 
}

// void *alloca(size_t size)
// {
// 	// return malloc(size);
// 	return __builtin_alloca(size);
// }

extern void __assert_fail(const char *assertion, const char *file, unsigned int line, const char *function) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__))
{
	printf("%s:%d: %s: Assertion %s failed", *file, line, *function, *assertion);
}
