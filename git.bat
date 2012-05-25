@echo off
:: Copyright (c) 2012 Marc-Antoine Ruel. All rights reserved.
:: Use of this source code is governed by a BSD-style license that can be
:: found in the LICENSE file.
setlocal
set PYTHONDONTWRITEBYTECODE=1
call python "%~dp0git_wrapper_tool.py" %*
