import React from 'react';

import Holding from './Holding';
import classes from './OrderList.module.css';
import Table from 'react-bootstrap/Table';

const Holdinglist = (props) => {

    let rows = []
    props.holdings.map((holding) => (
          rows.push(
            <tr>
                <td>{holding.symbol}</td>
                <td>{holding.shares}</td>
                <td>{holding.avg_price}</td>
            </tr>
          )
    ))

  return (
      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
            <th>Average Price</th>
          </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
      </Table>
  );
};

export default Holdinglist;
