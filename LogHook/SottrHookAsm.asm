.code

extern SottrAddr_RequestFile : dq
extern SottrAddr_GetAnimation : dq

extern SottrHandler_RequestFile : proc
extern SottrHandler_GetAnimation : proc

SottrHook_RequestFile proc
    mov rdx, rbx
    mov rcx, rbp
    sub rsp, 20h
    call SottrHandler_RequestFile
    add rsp, 20h
    jmp [SottrAddr_RequestFile]
SottrHook_RequestFile endp

SottrHook_GetAnimation proc
    push rcx
    push rdx
    push r8
    push r9

    lea rcx, [rax+rdi]
    sub rsp, 20h
    call SottrHandler_GetAnimation
    add rsp, 20h

    pop r9
    pop r8
    pop rdx
    pop rcx
    jmp [SottrAddr_GetAnimation]
SottrHook_GetAnimation endp

END
