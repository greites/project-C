DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS ProductHistory;
DROP TABLE IF EXISTS Sale;
DROP TABLE IF EXISTS SaleProduct;
DROP TABLE IF EXISTS Registry;
DROP TABLE IF EXISTS Note;
DROP TRIGGER IF EXISTS AddProductFromSale;
DROP TRIGGER IF EXISTS RemoveProductFromSale;
DROP TRIGGER IF EXISTS MinStockNote;

CREATE TABLE User (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserName TEXT UNIQUE NOT NULL,
    UserPermission TEXT UNIQUE NOT NULL,
    UserPassword TEXT NOT NULL
);


CREATE TABLE Product (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT, 
    ProductName TEXT UNIQUE NOT NULL,
    ProductPrice DECIMAL(10, 2) NOT NULL,
    ProductStock INTEGER NOT NULL,
    ProductMinStock INTEGER NOT NULL
);


CREATE TABLE Sale (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    SaleTotal DECIMAL(10,2) NOT NULL,
    SaleStatus TEXT NOT NULL DEFAULT 'OPEN',
    SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    --UserID INTEGER NOT NULL,
    --FOREIGN KEY (UserID) REFERENCES User(UserID)
);


CREATE TABLE SaleProduct (
    SaleID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Amount INTEGER NOT NULL,
    PRIMARY KEY (ProductID, SaleID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (SaleID) REFERENCES Sale(SaleID) ON DELETE CASCADE
);


CREATE TABLE Registry (
    RegistryID INTEGER PRIMARY KEY AUTOINCREMENT,
    RegistryDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Opening DECIMAL(10,2) NOT NULL,
    Closure DECIMAL(10,2) NOT NULL
);


CREATE TABLE Note (
    NoteID INTEGER PRIMARY KEY AUTOINCREMENT,
    NoteMessage TEXT NOT NULL,
    NoteStatus TEXT NOT NULL,
    NoteDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TRIGGER AddProductFromSale AFTER INSERT ON SaleProduct
FOR EACH ROW
BEGIN
    UPDATE Product
    SET ProductStock = ProductStock - NEW.Amount
    WHERE ProductID = NEW.ProductID;

    UPDATE Sale
    SET SaleTotal = SaleTotal + NEW.Amount * NEW.Price
    WHERE SaleID = NEW.SaleID;
END;


CREATE TRIGGER RemoveProductFromSale AFTER DELETE ON SaleProduct
FOR EACH ROW
BEGIN
    UPDATE Product
    SET ProductStock = ProductStock + OLD.Amount
    WHERE ProductID = OLD.ProductID;

    UPDATE Sale
    SET SaleTotal = SaleTotal - OLD.Amount * OLD.Price
    WHERE SaleID = OLD.SaleID;
END;


CREATE TRIGGER MinStockNote 
AFTER UPDATE OF ProductStock ON Product
FOR EACH ROW
BEGIN
    INSERT INTO Note (NoteMessage, NoteStatus) 
    SELECT 
        'The product "' || NEW.ProductName || '" is low in stock.',
        'unread'
    FROM Product
    WHERE ProductID = NEW.ProductID
    AND ProductStock <= ProductMinStock;
END;