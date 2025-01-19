using TrRebootTools.Shared.Cdc;

namespace TrRebootTools.Shared.Cdc
{
    public enum WwiseSoundBankItemReferenceType
    {
        DataIndex,
        Event
    }

    public record WwiseSoundBankItemReference(int BankResourceId, WwiseSoundBankItemReferenceType Type, int Index);
}
