

class ScrubParams(object):
    """Three Parameters for Scrubbing Process:
        - Stock Cutoff: Scrub all moves that are larger (absolute value) than the stock cutoff
        - Index Cutoff: Scrub all moves where the index move is smaller (absolute value) than the stock cutoff)
        - Percentile Cutoff: With the remaining data points, keep the n-percentile data points with the best fit on the OLS Regression.
        """
    def __init__(self,
                 stock_cutoff=5,
                 index_cutoff=0,
                 percentile_cutoff=100):
        
        self.stock_cutoff = stock_cutoff
        self.index_cutoff = index_cutoff
        self.percentile_cutoff = percentile_cutoff

    def __repr__(self):
        return "ScrubParams(Stock Cutoff: {:2f}, Index Cutoff: {:2f}, Percentile Cutoff: {:2f})".format(self.stock_cutoff, self.index_cutoff, self.percentile_cutoff)

