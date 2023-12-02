using System;
using System.Collections.Generic;
using System.ComponentModel;

namespace SottrModManager.Shared.Util
{
    public static class CollectionExtensions
    {
        public static TValue GetOrDefault<TKey, TValue>(this IDictionary<TKey, TValue> dict, TKey key)
        {
            dict.TryGetValue(key, out TValue value);
            return value;
        }

        public static TValue GetOrAdd<TKey, TValue>(this IDictionary<TKey, TValue> dict, TKey key, Func<TValue> createValue)
        {
            if (!dict.TryGetValue(key, out TValue value))
            {
                value = createValue();
                dict.Add(key, value);
            }
            return value;
        }

        public static void Deconstruct<TKey, TValue>(this KeyValuePair<TKey, TValue> pair, out TKey key, out TValue value)
        {
            key = pair.Key;
            value = pair.Value;
        }

        public static void AddRange<T>(this BindingList<T> list, IEnumerable<T> items)
        {
            foreach (T item in items)
            {
                list.Add(item);
            }
        }
    }
}
