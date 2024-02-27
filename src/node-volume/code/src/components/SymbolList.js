import React from 'react';

import Symbol from './Symbol';
import classes from './OrderList.module.css';

const SymbolList = (props) => {
  return (
    <ul className={classes['orders-list']}>
      {props.symbols.map((symbol) => (
        <Symbol
          name={symbol.name}
          price={symbol.price}
        />
      ))}
    </ul>
  );
};

export default SymbolList;
