#ifndef _ASM_IO_H
#define _ASM_IO_H

/*
 * This file contains parts of Linux's /usr/include/asm/io.h, but
 * with the argument order reversed for outb, outb_p, outw, outw_p.
 */

#define SLOW_DOWN_IO __asm__ __volatile__("outb %al,$0x80")

#define __OUT1(s,x) \
extern inline void __out##s(unsigned x value, unsigned short port); \
extern inline void __out##s(unsigned x value, unsigned short port) {

#define __OUT2(s,s1,s2) \
__asm__ __volatile__ ("out" #s " %" s1 "0,%" s2 "1"

#define __OUT(s,s1,x) \
__OUT1(s,x) __OUT2(s,s1,"w") : : "a" (value), "d" (port)); } \
__OUT1(s##c,x) __OUT2(s,s1,"") : : "a" (value), "id" (port)); } \
__OUT1(s##_p,x) __OUT2(s,s1,"w") : : "a" (value), "d" (port)); SLOW_DOWN_IO; } \
__OUT1(s##c_p,x) __OUT2(s,s1,"") : : "a" (value), "id" (port)); SLOW_DOWN_IO; }

#define __IN1(s) \
extern inline RETURN_TYPE __in##s(unsigned short port); \
extern inline RETURN_TYPE __in##s(unsigned short port) { RETURN_TYPE _v;

#define __IN2(s,s1,s2) \
__asm__ __volatile__ ("in" #s " %" s2 "1,%" s1 "0"

#define __IN(s,s1,i...) \
__IN1(s) __IN2(s,s1,"w") : "=a" (_v) : "d" (port) ,##i ); return _v; } \
__IN1(s##c) __IN2(s,s1,"") : "=a" (_v) : "id" (port) ,##i ); return _v; } \
__IN1(s##_p) __IN2(s,s1,"w") : "=a" (_v) : "d" (port) ,##i ); SLOW_DOWN_IO; return _v; } \
__IN1(s##c_p) __IN2(s,s1,"") : "=a" (_v) : "id" (port) ,##i ); SLOW_DOWN_IO; return _v; }

#define RETURN_TYPE unsigned char
/* __IN(b,"b","0" (0)) */
__IN(b,"")
#undef RETURN_TYPE
#define RETURN_TYPE unsigned short
/* __IN(w,"w","0" (0)) */
__IN(w,"")
#undef RETURN_TYPE
#define RETURN_TYPE unsigned int
__IN(l,"")
#undef RETURN_TYPE

__OUT(b,"b",char)
__OUT(w,"w",short)
__OUT(l,,int)

#define outb(port,val) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__outbc((val),(port)) : \
	__outb((val),(port)))

#define inb(port) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__inbc(port) : \
	__inb(port))

#define outb_p(port,val) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__outbc_p((val),(port)) : \
	__outb_p((val),(port)))

#define inb_p(port) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__inbc_p(port) : \
	__inb_p(port))

#define outw(port,val) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__outwc((val),(port)) : \
	__outw((val),(port)))

#define inw(port) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__inwc(port) : \
	__inw(port))

#define outw_p(port,val) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__outwc_p((val),(port)) : \
	__outw_p((val),(port)))

#define inw_p(port) \
((__builtin_constant_p((port)) && (port) < 256) ? \
	__inwc_p(port) : \
	__inw_p(port))

#endif