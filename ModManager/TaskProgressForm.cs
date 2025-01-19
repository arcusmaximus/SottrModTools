using System.ComponentModel;
using System.Threading;
using System.Windows.Forms;
using TrRebootTools.Shared;

namespace TrRebootTools.ModManager
{
    public partial class TaskProgressForm : Form, ITaskProgress
    {
        private readonly CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
        private bool _active;

        public TaskProgressForm()
        {
            InitializeComponent();
        }

        public void Begin(string statusText)
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => Begin(statusText)));
                return;
            }

            Text = statusText;
            _progressBar.Value = 0;
            _active = true;
        }

        public void Report(float progress)
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => Report(progress)));
                return;
            }

            _progressBar.Value = (int)(progress * _progressBar.Maximum);
        }

        public void End()
        {
            if (InvokeRequired)
            {
                Invoke(new MethodInvoker(() => End()));
                return;
            }

            _active = false;
        }

        public CancellationToken CancellationToken => _cancellationTokenSource.Token;

        protected override void OnClosing(CancelEventArgs e)
        {
            base.OnClosing(e);
            if (!_active)
                return;

            e.Cancel = true;
            Text = "Canceling...";
            _cancellationTokenSource.Cancel();
        }
    }
}
