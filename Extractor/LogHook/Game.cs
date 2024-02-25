using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace SottrExtractor.LogHook
{
    internal class Game : IDisposable
    {
        public static readonly Version ExpectedVersion = new Version(1, 0, 492);

        [DllImport("kernel32")]
        private static extern IntPtr GetModuleHandleW([MarshalAs(UnmanagedType.LPWStr)] string lpModuleName);

        [DllImport("kernel32")]
        private static extern IntPtr GetProcAddress(IntPtr hModule, [MarshalAs(UnmanagedType.LPStr)] string lpProcName);

        [DllImport("kernel32")]
        private static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, int flAllocationType, int flProtect);

        [DllImport("kernel32")]
        private static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, int dwFreeType);

        [DllImport("kernel32")]
        private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, [MarshalAs(UnmanagedType.LPArray)] byte[] lpBuffer, int nSize, IntPtr lpNumberOfBytesWritten);

        [DllImport("kernel32")]
        private static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, int dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, int dwCreationFlags, out int lpThreadId);

        [DllImport("kernel32")]
        private static extern int WaitForSingleObject(IntPtr hHandle, int dwMilliseconds);


        private const int MEM_COMMIT = 0x00001000;
        private const int MEM_RELEASE = 0x00008000;

        private const int PAGE_READWRITE = 0x04;
        private const int PAGE_EXECUTE = 0x10;


        private readonly string _exePath;
        private readonly CancellationTokenSource _cancellationTokenSource;
        private Task _eventListenTask;

        public Game(string exePath)
        {
            _exePath = exePath;
            _cancellationTokenSource = new CancellationTokenSource();
            Events = new NotificationChannel();
        }

        public void Start()
        {
            const string dllName = "SottrLogHook.dll";
            string dllPath = Path.Combine(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), dllName);
            if (!File.Exists(dllPath))
                throw new Exception($"{dllName} is missing in the extractor's installation directory");

            using Process process = Process.Start(
                new ProcessStartInfo
                {
                    FileName = _exePath,
                    WorkingDirectory = Path.GetDirectoryName(_exePath),
                    UseShellExecute = false
                }
            );
            Thread.Sleep(1000);

            if (!LoadDllIntoProcess(process.Handle, dllPath))
                throw new Exception($"Failed to inject {dllName} into process");

            _eventListenTask = Task.Run(() => Events.Listen(_cancellationTokenSource.Token));
        }

        public NotificationChannel Events
        {
            get;
        }

        private static bool LoadDllIntoProcess(IntPtr hProcess, string dllPath)
        {
            IntPtr hKernel32 = GetModuleHandleW("kernel32");
            IntPtr pLoadLibraryW = GetProcAddress(hKernel32, "LoadLibraryW");

            byte[] dllPathBytes = Encoding.Unicode.GetBytes(dllPath);
            byte[] code = new byte[0x28 + dllPathBytes.Length + 2];
            IntPtr pCode = VirtualAllocEx(hProcess, IntPtr.Zero, code.Length, MEM_COMMIT, PAGE_EXECUTE);
            if (pCode == IntPtr.Zero)
                return false;

            // push rbp
            code[0x0] = 0x55;

            // mov rbp, rsp
            code[0x1] = 0x48;
            code[0x2] = 0x89;
            code[0x3] = 0xE5;
            
            // and rsp, ~0xF
            code[0x4] = 0x48;
            code[0x5] = 0x83;
            code[0x6] = 0xE4;
            code[0x7] = 0xF0;

            // mov rcx, offset dllPath
            code[0x8] = 0x48;
            code[0x9] = 0xB9;
            Array.Copy(BitConverter.GetBytes(pCode.ToInt64() + 0x28), 0, code, 0xA, 8);

            // mov rax, offset LoadLibraryW
            code[0x12] = 0x48;
            code[0x13] = 0xB8;
            Array.Copy(BitConverter.GetBytes(pLoadLibraryW.ToInt64()), 0, code, 0x14, 8);
            
            // sub rsp, 0x20
            code[0x1C] = 0x48;
            code[0x1D] = 0x83;
            code[0x1E] = 0xEC;
            code[0x1F] = 0x20;

            // call rax
            code[0x20] = 0xFF;
            code[0x21] = 0xD0;

            // mov rsp, rbp
            code[0x22] = 0x48;
            code[0x23] = 0x89;
            code[0x24] = 0xEC;

            // pop rbp
            code[0x25] = 0x5D;

            // ret
            code[0x26] = 0xC3;

            // DLL path
            Array.Copy(dllPathBytes, 0, code, 0x28, dllPathBytes.Length);

            try
            {
                if (!WriteProcessMemory(hProcess, pCode, code, code.Length, IntPtr.Zero))
                    return false;

                IntPtr hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, pCode, IntPtr.Zero, 0, out _);
                if (hThread == IntPtr.Zero)
                    return false;

                if (WaitForSingleObject(hThread, 5000) != 0)
                    return false;

                return true;
            }
            finally
            {
                VirtualFreeEx(hProcess, pCode, 0, MEM_RELEASE);
            }
        }

        public void Dispose()
        {
            if (_eventListenTask != null)
            {
                _cancellationTokenSource.Cancel();
                _eventListenTask.Wait();
                _eventListenTask = null;
            }
            Events.Dispose();
        }
    }
}
