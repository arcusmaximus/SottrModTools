namespace SottrModManager.Shared.Cdc
{
    public enum WwiseSoundBankItemReferenceType
    {
        DataIndex,
        Event
    }

    public record WwiseSoundBankItemReference(int BankResourceId, WwiseSoundBankItemReferenceType Type, int Index);
}
