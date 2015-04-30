tp
==

tp was a challenge consisting of two parts, in total woth 620 points. For PlaidCTF we (KITCTF) teamed up with StratumAuhuur as "Eat Sleep Pwn Repeat" and me and [@_tsuro](https://twitter.com/_tsuro) worked together to solve this challenge during the CTF.

checksec.sh reports all protections as beeing enabled. Running the binary results in no noticeable output and our input seems to be ignored as well. Time for some reversing.

##Reverse Engineering

The binary does some not exactly trivial sandboxing setup. Here is what happens:

At first, the parent and child process set up a "trusted" code and stack region as follows:

- After forking, the child mmaps a huge rwx memory region (0x10000000 - 0x700000000000)
- The parent then (u)randomly chooses two regions inside that mapped region, one becomes the "trusted code", the other the "trusted stack"
- The parent sends the addresses of these two regions to the child by means of a process\_vm\_writev call
- The child continues executing in the trusted code trough a swapcontext call
- The child starts a second thread which will continue executing the "untrusted" code

At this point the parent's job is done and it will wait for a timeout set via a call to alarm() and kill the child.

The child now sets up the sandbox:
- It initializes a seccomp BPF sandbox, only allowing read, write, clone, exit, sigreturn, sigprocmask _and_ any syscall from a specific "syscall" instruction in the trusted code region
- If a syscall fails, control is transferred to a SIGSYS handler which communicates with the trusted thread trough two pipes. It will request execution of the failed syscall
    - The trusted code validates the syscall a second time, now allowing mmap, mprotect, munmap, brk, and mremap - probably in an effort to support memory allocation - then either aborts the process or executes the syscall on behalf of the untrusted thread. In the latter case execution continues in the untrusted thread as if the syscall suceeded the first time
    - The sandbox basically relies on the additional ASLR of the trusted code + stack that the parent process set up

After this is done, the second thread begins executing the actual uesr facing code. TODO
The binary implements a kind of note storage and uses a binary protocol. Notes can be created, updated, read and deleted and are stored in what looks like a c++ std::set.

##Bug discovery

The "normal" control flow looks pretty solid, there don't seem to be any overflows or similar. However, there are some exception handlers in place, making sure the code can continue to run even after out-of-memory exceptions or similar. This is interesting as it may lead to memory corruption if some data structure is in the process of being modified when an exception occurs. There is one specific exception handler, used when adding a new note, in pseudo c++:

```c++
void add_note()
{
    Note* note;
    try {
        Note* note; = new Note;
        build_and_insert_note(note);
    } catch {
        delete note;
    }

    // ...
}
```

the build_and_insert_note() function is responsible for populating and inserting the passed note structure:

```c++
void build_and_insert_note(Note* note)
{
    note->id = note_counter++;
    note->in_use = 1;
    
    notes.add(note);        // global set of notes

    note->size = read_note_size();
    note->data = new char[](note->size);

    // ...
}
```

So, if we supply a large enough size, new/malloc will fail, throwing an exception and effectively causing a Use-After-Free condition as the freed note object is still in the set. Nice.
     

##Exploitation, Part 1 (first flag)

For flag 1 we "only" need code execution inside the sandbox as the trusted code allows an open syscall if the path is "/home/tp/flag1".
After triggering the UAF we can update a previously allocated note so a new heap block is allocated to store the content -- it will be placed in the same block that is still linked in the set. At this point we basically have an arbitrary read + write as we can set the id, size and pointer value of the victim chunk and then update/read the note with the new id, however, we do need an info leak as the binary is full PIE.

Constructing an info leak is possible in the following way:
We can set the id of the victim chunk to some known value, set the size to 1 or similar and the pointer to 0, then update the chunk with that id, causing a heap pointer to be written into the chunk which we can subsequently leak. Afterwards we will find some pointers into the binaries .text at the end of the current page (didn't investigate why, but seems very reliable).

To finish this part we can get the location of the "untrusted" stack from ld (\_\_libc\_stack\_end), then directly overwrite saved EIP and put a little ropchain on the stack to map RWX memory (mmap is allowed by the userspace syscall filter) and execute our shellcode which then sends us the flag. 420 points.

##Exploitation, Part 2 (second flag)

Escaping the sandbox basically boils down to learning the address of the trusted code and/or stack in memory. There seem to be at least two different ways to do this:

###1 mmap

This is not perfectly reliable but works (and is what we did during the CTF). When we try to map a huge memory region, mmap finds the mapping we are looking for to be in the way and will then place the new mapping behind the existing one. So, with some luck, if we mmap a new region it will be some pages behind either the trusted code or the trusted stack region. From there we can go backwards in page steps and see if the current page is mapped using mprotect.

###2 mremap

Using mremap we can perform a binary search by trying to remap a large section. This will fail if there is no mapping in there.
