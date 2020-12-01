import React from "react";
import PropTypes from "prop-types";
import { useTable, useExpanded } from "react-table";

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

function usePuzzleTable({ columns, data }) {
    const {
        getTableProps,
        getTableBodyProps,
        allColumns,
        rows,
        prepareRow,
    } = useTable(
        {
            columns,
            data,
        },
        useExpanded);

    return (
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
    );
}

