using System;
using System.Collections.Generic;

namespace ThornWhip
{
    // Nominal resource value, in silver. Based on CE/RimWorld's conventional resources.
    // Only used for market valuation; actual payment uses real stacks and exact quantities.
    // Trading prices still follow vanilla trader and storyteller factors.
    public static class EconomyBalance
    {
        public static float MinimumFinishedValue(IEnumerable<KeyValuePair<string, int>> materials)
        {
            float total = 0f;
            if (materials == null) return 0f;
            foreach (var line in materials)
            {
                if (line.Value <= 0) continue;
                float silver = 0f;
                switch (line.Key)
                {
                    case "Steel": silver = 1.9f; break;
                    case "Plasteel": silver = 9.0f; break;
                    case "Uranium": silver = 6.0f; break;
                    case "ComponentIndustrial": silver = 32.0f; break;
                    case "ComponentSpacer": silver = 200.0f; break;
                    case "Gold": silver = 10.0f; break;
                }
                total += silver * line.Value;
            }
            // Price floor only: prevents a 9k-silver advanced module being worth 3k on sale.
            // 1.12 covers a modest part of skilled labor, not a free profit at every trader.
            return total * 1.12f;
        }
    }
}
