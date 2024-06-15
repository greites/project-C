INSERT INTO Product (ProductName, ProductPrice, ProductStock, ProductMinStock) VALUES
  ('Orange', '0.99', '80', '35'),
  ('Banana', '0.79', '70', '25');

INSERT INTO Sale (SaleTotal) VALUES 
  ('0');

INSERT INTO SaleProduct (SaleID, ProductID, Price, Amount) VALUES 
  ('1', '2', '0.79', '10');  