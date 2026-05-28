"""FR-24: CLI entry point for the I Fetch Rocks simulator.

Usage:
    python -m ifetchrocks.sim.cli <command> [options]

Commands:
    step N              Run N instructions, print final state
    trace N             Run N instructions, print each one
    backtrace PREFIX    Print wire backtrace
    forwardtrace PREFIX Print wire forwardtrace
    inspect UUID_PREFIX Print device inspection report
    probe W1 [W2..] --ticks N   Multi-wire probe table
    heatmap [--start N] [--end N]   Execution heatmap
    health              Run circuit health check
    path SRC DST        Find signal path between two wires
"""
from __future__ import annotations

import os
import sys
from typing import TextIO

# Career save UUID used as default
DEFAULT_SAVE_UUID = 'd88a1650-10b4-4d00-8c31-f69b4b41dee2'

COMMANDS = {
    'step': 'Run N instructions, print final state',
    'trace': 'Run N instructions, print each one',
    'backtrace': 'Print wire backtrace for PREFIX',
    'forwardtrace': 'Print wire forwardtrace for PREFIX',
    'inspect': 'Print device inspection report for UUID_PREFIX',
    'probe': 'Multi-wire probe table (needs --ticks N)',
    'heatmap': 'Print execution heatmap',
    'health': 'Run circuit health check',
    'path': 'Find signal path between SRC and DST wires',
    'repl': 'Launch interactive REPL',
    'listing': 'Print annotated program listing [--pc N]',
}


def _print_usage(out: TextIO) -> None:
    out.write('Usage: python -m ifetchrocks.sim.cli <command> [options]\n\n')
    out.write('Commands:\n')
    for cmd, desc in COMMANDS.items():
        out.write(f'  {cmd:20s} {desc}\n')
    out.write('\nOptions:\n')
    out.write('  --save UUID          Save file UUID (default: career save)\n')
    out.write('  --help               Show this help\n')


def _find_save_path(uuid: str) -> str:
    """Locate the save file, trying common base directories."""
    candidates = [
        os.path.join('game_app_data', 'Saves', f'{uuid}.json'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', '..', '..', 'game_app_data', 'Saves', f'{uuid}.json'),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]  # return first candidate for error message


def _load_mainasm():
    """Import mainasm, suppressing its import-time stdout output."""
    import io as _io
    old_stdout = sys.stdout
    sys.stdout = _io.StringIO()
    try:
        from ifetchrocks.programs import mainasm
        return mainasm
    finally:
        sys.stdout = old_stdout


def _load_simulator(save_uuid: str | None = None):
    """Load a Simulator from the given save UUID."""
    from ifetchrocks_sim.simulator import Simulator
    uuid = save_uuid or DEFAULT_SAVE_UUID
    path = _find_save_path(uuid)
    sim = Simulator()
    with open(path) as f:
        sim.load_from_file(f)
    return sim


def _load_debugger(save_uuid: str | None = None):
    """Load a SimulatorDebugger with mainasm program and power on."""
    # Suppress any stdout during mainasm import
    import io as _io
    old_stdout = sys.stdout
    sys.stdout = _io.StringIO()
    try:
        from ifetchrocks.programs import mainasm
    finally:
        sys.stdout = old_stdout

    from ifetchrocks.sim.debugger import SimulatorDebugger
    sim = _load_simulator(save_uuid)
    return SimulatorDebugger.for_career_save(sim, mainasm.iw)


def _parse_global_opts(args: list[str]) -> tuple[dict, list[str]]:
    """Extract --save UUID from args, return (opts, remaining_args)."""
    opts = {'save': None}
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == '--save' and i + 1 < len(args):
            opts['save'] = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    return opts, remaining


def _cmd_step(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if not args:
        stderr.write('Error: step requires a count N\n')
        return 1
    try:
        n = int(args[0])
    except ValueError:
        stderr.write(f'Error: invalid count: {args[0]}\n')
        return 1
    if n < 1:
        stderr.write('Error: count must be >= 1\n')
        return 1

    dbg = _load_debugger(opts['save'])
    for _ in range(n):
        snaps = dbg.step_instruction()
    old = sys.stdout
    sys.stdout = stdout
    try:
        dbg.print_state(snaps[-1])
    finally:
        sys.stdout = old
    return 0


def _cmd_trace(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if not args:
        stderr.write('Error: trace requires a count N\n')
        return 1
    try:
        n = int(args[0])
    except ValueError:
        stderr.write(f'Error: invalid count: {args[0]}\n')
        return 1

    dbg = _load_debugger(opts['save'])
    for i in range(n):
        snaps = dbg.step_instruction()
        snap = snaps[-1]
        stdout.write(f'{str(snap)}\n')
    return 0


def _cmd_backtrace(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if not args:
        stderr.write('Error: backtrace requires a wire prefix\n')
        return 1
    prefix = args[0]
    sim = _load_simulator(opts['save'])
    old = sys.stdout
    sys.stdout = stdout
    try:
        sim.print_backtrace(prefix)
    finally:
        sys.stdout = old
    return 0


def _cmd_forwardtrace(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if not args:
        stderr.write('Error: forwardtrace requires a wire prefix\n')
        return 1
    prefix = args[0]
    sim = _load_simulator(opts['save'])
    old = sys.stdout
    sys.stdout = stdout
    try:
        sim.print_forwardtrace(prefix)
    finally:
        sys.stdout = old
    return 0


def _cmd_inspect(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if not args:
        stderr.write('Error: inspect requires a device UUID prefix\n')
        return 1
    from ifetchrocks.sim.debugger import print_device
    prefix = args[0]
    sim = _load_simulator(opts['save'])
    print_device(sim, prefix, file=stdout)
    return 0


def _cmd_probe(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    # Parse wire prefixes and --ticks N
    wire_prefixes = []
    ticks = None
    i = 0
    while i < len(args):
        if args[i] == '--ticks' and i + 1 < len(args):
            try:
                ticks = int(args[i + 1])
            except ValueError:
                stderr.write(f'Error: invalid tick count: {args[i + 1]}\n')
                return 1
            i += 2
        else:
            wire_prefixes.append(args[i])
            i += 1

    if not wire_prefixes:
        stderr.write('Error: probe requires at least one wire prefix\n')
        return 1
    if ticks is None:
        stderr.write('Error: probe requires --ticks N\n')
        return 1

    from ifetchrocks.sim.debugger import probe_wires, print_probe_table
    dbg = _load_debugger(opts['save'])
    table = probe_wires(dbg.sim, wire_prefixes, range(ticks))
    print_probe_table(table, file=stdout)
    return 0


def _cmd_heatmap(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    start = None
    end = None
    run_n = 100  # default instructions to run before printing heatmap
    i = 0
    while i < len(args):
        if args[i] == '--start' and i + 1 < len(args):
            start = int(args[i + 1])
            i += 2
        elif args[i] == '--end' and i + 1 < len(args):
            end = int(args[i + 1])
            i += 2
        elif args[i] == '--run' and i + 1 < len(args):
            run_n = int(args[i + 1])
            i += 2
        else:
            i += 1

    dbg = _load_debugger(opts['save'])
    # Run some instructions to build up heatmap data
    for _ in range(run_n):
        try:
            dbg.step_instruction()
        except Exception:
            break
    dbg.print_heatmap(start=start, end=end, file=stdout)
    return 0


def _cmd_health(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    from ifetchrocks_sim.validation import health_check
    sim = _load_simulator(opts['save'])
    report = health_check(sim)
    stdout.write(report.summary())
    stdout.write('\n')
    return 0


def _cmd_path(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    if len(args) < 2:
        stderr.write('Error: path requires SRC and DST wire prefixes\n')
        return 1
    src, dst = args[0], args[1]
    sim = _load_simulator(opts['save'])
    result = sim.find_signal_path(src, dst)
    if result is None:
        stdout.write(f'No path found from {src} to {dst}\n')
    else:
        for item in result:
            stdout.write(f'  {item}\n')
    return 0


def _cmd_repl(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    from ifetchrocks_sim.repl import SimulatorRepl
    dbg = _load_debugger(opts['save'])
    repl = SimulatorRepl(dbg, output=stdout)
    repl.run()
    return 0


def _cmd_listing(args: list[str], opts: dict, stdout: TextIO, stderr: TextIO) -> int:
    pc = None
    i = 0
    while i < len(args):
        if args[i] == '--pc' and i + 1 < len(args):
            try:
                pc = int(args[i + 1])
            except ValueError:
                stderr.write(f'Error: invalid PC value: {args[i + 1]}\n')
                return 1
            i += 2
        else:
            i += 1
    mainasm = _load_mainasm()
    sm = mainasm.iw.get_source_map()
    stdout.write(sm.format_listing(highlight_pc=pc))
    stdout.write('\n')
    return 0


DISPATCH = {
    'step': _cmd_step,
    'trace': _cmd_trace,
    'backtrace': _cmd_backtrace,
    'forwardtrace': _cmd_forwardtrace,
    'inspect': _cmd_inspect,
    'probe': _cmd_probe,
    'heatmap': _cmd_heatmap,
    'health': _cmd_health,
    'path': _cmd_path,
    'repl': _cmd_repl,
    'listing': _cmd_listing,
}


def main(args: list[str] | None = None,
         stdout: TextIO | None = None,
         stderr: TextIO | None = None) -> int:
    """CLI entry point. Returns exit code (0 = success)."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    if args is None:
        args = sys.argv[1:]

    if not args or args == ['--help']:
        _print_usage(stdout if args == ['--help'] else stderr)
        return 0 if args == ['--help'] else 1

    opts, remaining = _parse_global_opts(args)

    if not remaining:
        _print_usage(stderr)
        return 1

    command = remaining[0]
    cmd_args = remaining[1:]

    if command not in DISPATCH:
        stderr.write(f'Error: unknown command: {command}\n')
        _print_usage(stderr)
        return 1

    try:
        return DISPATCH[command](cmd_args, opts, stdout, stderr)
    except FileNotFoundError as e:
        stderr.write(f'Error: {e}\n')
        return 1
    except Exception as e:
        stderr.write(f'Error: {e}\n')
        return 1


if __name__ == '__main__':
    sys.exit(main())
