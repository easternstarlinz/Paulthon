Here, I outline step by step how I calculate my betas.
    -Part 1: How I calculate beta for a given stock and ETF.
    -Part 2 is simple: For a given stock, I run the beta calculation (Part 1) for each ETF candidate. I deem the "Best Beta" as the ETF pairing that produces the highest R^2 value.


Part 1:
    A)
        -Set CutoffParams:
            -STD_Cutoff_Stock-- (this number) * (STD of the stock returns) = Stock Pct Cutoff
            -STD_Cutoff_Index -- (this number) * (STD of the index returns) = Index Pct Cutoff
            -Percentile_Cutoff: For the HV calculation, eliminate biggest moves above the percentile cutoff
                -Value of 90 would eliminate the 10% biggest moves for the HV calculation.

        -ScrubParams
            -Stock Pct Cutoff -- Eliminate data points where the stock moved MORE than this cutoff.
            -Index Pct Cutoff-- Eliminate data points where the index moved LESS than this cutoff.
            -Percentile Cutoff -- Keep only the data points with the highest quality fit
                -Value of .80 -- would remove the 20% worst fitting data points and re-calculate beta
        
