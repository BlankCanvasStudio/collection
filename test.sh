#!/bin/bash

set -x

# echo mrg new experiment init.blankcanvas
mrg new experiment init.blankcanvas

sleep 5

set -e

rev=$(mrg push ./models/discern.model init.blankcanvas | head -1 | awk '{print $4}')
echo "revision: $rev"

sleep 5

mrg realize test.init.blankcanvas revision $rev

sleep 2

mrg materialize test.init.blankcanvas

sleep 2

mrg new xdc test.blankcanvas || true

sleep 2

mrg xdc attach test.blankcanvas test.init.blankcanvas
