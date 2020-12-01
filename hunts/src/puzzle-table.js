import React from "react";
import PropTypes from "prop-types";
import { useTable, useExpanded } from "react-table";
import { useGlobalFilter } from "./use-global-filter-fixed.js";
import { matchSorter } from "match-sorter";

export function PuzzleTable({ columns, data }) {
    return usePuzzleTable({
        columns: React.useMemo(() => columns, [columns]),
        data: React.useMemo(() => data, [data]),
    });
}

PuzzleTable.propTypes = {
    columns: PropTypes.array.isRequired,
    data: PropTypes.array.isRequired,
};

function textFilterFn(rows, id, filterValue) {
    // Need to clone these results because this library is broken as shit
    return matchSorter(rows, filterValue, { 
        keys: ["values.name", "values.tags", "values.status", "values.answer"]
    }).map(row => Object.assign({}, row));
}

textFilterFn.autoRemove = val => !val;

function usePuzzleTable({ columns, data }) {
    const filterTypes = React.useMemo(
        () => ({
            globalFilter: textFilterFn,
        }),
        []
    );

    const {
        getTableProps,
        getTableBodyProps,
        allColumns,
        rows,
        state,
        prepareRow,
        toggleAllRowsExpanded,
        flatRows,
        preGlobalFilteredRows,
        setGlobalFilter,
    } = useTable(
        {
            columns,
            data,
            filterTypes,
            autoResetExpanded: false,
            globalFilter: "globalFilter",
        },
        useGlobalFilter,
        useExpanded,
    );

    React.useMemo(() => toggleAllRowsExpanded(true), [data]);

    return (
        <>
            <GlobalFilter
                globalFilter={state.globalFilter}
                setGlobalFilter={setGlobalFilter}
            />
            <table {...getTableProps()}>
                <thead>
                    <tr>
                        {allColumns.map(column => (
                            <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                        ))}
                    </tr>
                </thead>
                <tbody {...getTableBodyProps()}>
                    {rows.map((row, i) => {
                        prepareRow(row);
                        return (
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => {
                                    return <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                                })}
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </>
    );
}

function GlobalFilter({
    globalFilter,
    setGlobalFilter,
}) {
    const [value, setValue] = React.useState(globalFilter);

    return (
        <span>
            <input
                value={value || ""}
                onChange={e => {
                    setValue(e.target.value);
                    setGlobalFilter(e.target.value);
                }}      
                placeholder={"Search"}
            />
        </span>
    )
}
