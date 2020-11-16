#!/usr/bin/env python3
# from https://github.com/ricklupton/floweaver/blob/master/docs/tutorials/quickstart.ipynb
import floweaver as fw
import pandas as pd
flows = pd.read_csv('simple_fruit_sales.csv')

if __name__ == "__main__":

   # Set the default size to fit the documentation better.
    size = dict(width=570, height=300)

    nodes = {
        "farms": fw.ProcessGroup(["farm1", "farm2", "farm3", "farm4", "farm5", "farm6"]),
        "customers": fw.ProcessGroup(["James", "Mary", "Fred", "Susan"]),
    }

    ordering = [
        ["farms"],  # put "farms" on the left...
        ["customers"],  # ... and "customers" on the right.
    ]

    bundles = [
        fw.Bundle("farms", "customers"),
    ]

    sdd = fw.SankeyDefinition(nodes, bundles, ordering)
    widget = fw.weave(sdd, flows).to_widget(**size)

    farms_with_other = fw.Partition.Simple(
        "process",
        [
            "farm1",  # the groups within the partition can be a single id...
            "farm2",
            "farm3",
            ("other", ["farm4", "farm5", "farm6"]),  # ... or a group
        ],
    )

    # This is another partition.
    customers_by_name = fw.Partition.Simple("process", ["James", "Mary", "Fred", "Susan"])

    # Update the ProcessGroup nodes to use the partitions
    nodes["farms"].partition = farms_with_other
    nodes["customers"].partition = customers_by_name

    # New Sankey!
    fw.weave(sdd, flows).to_widget(**size)
