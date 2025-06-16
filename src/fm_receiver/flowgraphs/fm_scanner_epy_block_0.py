"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr



class blk(gr.sync_block):
    def __init__(self, threshold_value=0.5, vector_length=1024):
        """
        Args:
            threshold_value: Threshold below which values are zeroed.
            vector_length: Length of the float vector.
        """
        gr.sync_block.__init__(
            self,
            name='Vector Threshold',
            in_sig=[(np.float32, vector_length)],
            out_sig=[(np.float32, vector_length)],
        )
        self.threshold = threshold_value
        self.vector_length = vector_length

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        # Apply thresholding: zero values below threshold
        out[:] = np.where(in0 >= self.threshold, in0, 0.0)

        return len(output_items[0])
