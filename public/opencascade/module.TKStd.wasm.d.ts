declare const libName = "./module.TKStd.wasm.d.ts";
export default libName;

type Standard_Boolean = boolean;
type Standard_Byte = number;
type Standard_Character = number;
type Standard_CString = string;
type Standard_Integer = number;
type Standard_Real = number;
type Standard_ShortReal = number;
type Standard_Size = number;

export declare class ShapePersistent {
  constructor();
  static BindTypes(theMap: StdObjMgt_MapOfInstantiators): void;
  delete(): void;
}

export declare class StdPersistent_TopoDS {
  constructor();
  delete(): void;
}

export declare class StdObject_Location {
  constructor();
  PChildren(theChildren: any): void;
  Import(): TopLoc_Location;
  static Translate(theLoc: TopLoc_Location, theMap: StdObjMgt_TransientPersistentMap): StdObject_Location;
  delete(): void;
}

export declare class StdObject_Shape {
  constructor()
  Import(): TopoDS_Shape;
  PChildren(theChildren: any): void;
  delete(): void;
}

export declare class StdPersistent_HArray1 {
  constructor();
  delete(): void;
}

export declare class ShapePersistent_HArray1 {
  constructor();
  delete(): void;
}

export declare class ShapePersistent_HArray2 {
  constructor();
  delete(): void;
}

export declare class ShapePersistent_HSequence {
  constructor();
  delete(): void;
}

export declare class StdDrivers {
  constructor();
  static Factory(aGUID: Standard_GUID): any;
  static DefineFormat(theApp: any): void;
  static BindTypes(theMap: StdObjMgt_MapOfInstantiators): void;
  delete(): void;
}

export declare class StdDrivers_DocumentRetrievalDriver extends StdLDrivers_DocumentRetrievalDriver {
  constructor();
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class StdPersistent {
  constructor();
  static BindTypes(theMap: StdObjMgt_MapOfInstantiators): void;
  delete(): void;
}

export declare class StdPersistent_DataXtd {
  constructor();
  delete(): void;
}

export declare class StdPersistent_DataXtd_Constraint {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(theChildren: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdPersistent_DataXtd_PatternStd {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(theChildren: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdPersistent_Naming {
  constructor();
  delete(): void;
}

export declare class StdPersistent_PPrsStd {
  constructor();
  delete(): void;
}

export declare class StdStorage {
  constructor();
  static Version(): TCollection_AsciiString;
  static Read_1(theFileName: TCollection_AsciiString, theData: any): Storage_Error;
  static Read_2(theDriver: any, theData: any): Storage_Error;
  static Write(theDriver: any, theData: any): Storage_Error;
  delete(): void;
}

export declare class StdStorage_Bucket {
  Clear(): void;
  delete(): void;
}

  export declare class StdStorage_Bucket_1 extends StdStorage_Bucket {
    constructor();
  }

  export declare class StdStorage_Bucket_2 extends StdStorage_Bucket {
    constructor(theSpaceSize: Standard_Integer);
  }

export declare class StdStorage_BucketOfPersistent {
  constructor(theBucketSize: Standard_Integer, theBucketNumber: Standard_Integer)
  Length(): Standard_Integer;
  Append(sp: any): void;
  Value(theIndex: Standard_Integer): StdObjMgt_Persistent;
  Clear(): void;
  delete(): void;
}

export declare class StdStorage_BucketIterator {
  constructor(a: StdStorage_BucketOfPersistent)
  Init(a0: StdStorage_BucketOfPersistent): void;
  Reset(): void;
  Value(): StdObjMgt_Persistent;
  More(): Standard_Boolean;
  Next(): void;
  delete(): void;
}

export declare class StdStorage_Data extends Standard_Transient {
  constructor()
  Clear(): void;
  HeaderData(): any;
  TypeData(): any;
  RootData(): any;
  delete(): void;
}

export declare class StdStorage_Root extends Standard_Transient {
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  Name(): TCollection_AsciiString;
  SetName(theName: TCollection_AsciiString): void;
  Object(): any;
  SetObject(anObject: any): void;
  Type(): TCollection_AsciiString;
  SetType(aType: TCollection_AsciiString): void;
  Reference(): Standard_Integer;
  delete(): void;
}

  export declare class StdStorage_Root_1 extends StdStorage_Root {
    constructor();
  }

  export declare class StdStorage_Root_2 extends StdStorage_Root {
    constructor(theName: TCollection_AsciiString, theObject: any);
  }

export declare class StdStorage_HeaderData extends Standard_Transient {
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  Read(theDriver: any): Standard_Boolean;
  Write(theDriver: any): Standard_Boolean;
  CreationDate(): TCollection_AsciiString;
  StorageVersion(): TCollection_AsciiString;
  SchemaVersion(): TCollection_AsciiString;
  SetApplicationVersion(aVersion: TCollection_AsciiString): void;
  ApplicationVersion(): TCollection_AsciiString;
  SetApplicationName(aName: TCollection_ExtendedString): void;
  ApplicationName(): TCollection_ExtendedString;
  SetDataType(aType: TCollection_ExtendedString): void;
  DataType(): TCollection_ExtendedString;
  AddToUserInfo(theUserInfo: TCollection_AsciiString): void;
  UserInfo(): TColStd_SequenceOfAsciiString;
  AddToComments(aComment: TCollection_ExtendedString): void;
  Comments(): TColStd_SequenceOfExtendedString;
  NumberOfObjects(): Standard_Integer;
  ErrorStatus(): Storage_Error;
  ErrorStatusExtension(): TCollection_AsciiString;
  ClearErrorStatus(): void;
  SetNumberOfObjects(anObjectNumber: Standard_Integer): void;
  SetStorageVersion(aVersion: TCollection_AsciiString): void;
  SetCreationDate(aDate: TCollection_AsciiString): void;
  SetSchemaVersion(aVersion: TCollection_AsciiString): void;
  SetSchemaName(aName: TCollection_AsciiString): void;
  delete(): void;
}

export declare class StdStorage_RootData extends Standard_Transient {
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  Read(theDriver: any): Standard_Boolean;
  Write(theDriver: any): Standard_Boolean;
  NumberOfRoots(): Standard_Integer;
  AddRoot(aRoot: any): void;
  Roots(): any;
  Find(aName: TCollection_AsciiString): any;
  IsRoot(aName: TCollection_AsciiString): Standard_Boolean;
  RemoveRoot(aName: TCollection_AsciiString): void;
  ErrorStatus(): Storage_Error;
  ErrorStatusExtension(): TCollection_AsciiString;
  ClearErrorStatus(): void;
  Clear(): void;
  delete(): void;
}

export declare class StdStorage_TypeData extends Standard_Transient {
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  Read(theDriver: any): Standard_Boolean;
  Write(theDriver: any): Standard_Boolean;
  NumberOfTypes(): Standard_Integer;
  AddType_1(aTypeName: TCollection_AsciiString, aTypeNum: Standard_Integer): void;
  AddType_2(aPObj: any): Standard_Integer;
  Type_1(aTypeNum: Standard_Integer): TCollection_AsciiString;
  Type_2(aTypeName: TCollection_AsciiString): Standard_Integer;
  Instantiator(aTypeNum: Standard_Integer): any;
  IsType(aName: TCollection_AsciiString): Standard_Boolean;
  Types(): any;
  ErrorStatus(): Storage_Error;
  ErrorStatusExtension(): TCollection_AsciiString;
  ClearErrorStatus(): void;
  Clear(): void;
  delete(): void;
}

export declare class Handle_StdPersistent_HArray1OfShape1 {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdPersistent_HArray1OfShape1): void;
  get(): StdPersistent_HArray1OfShape1;
  delete(): void;
}

  export declare class Handle_StdPersistent_HArray1OfShape1_1 extends Handle_StdPersistent_HArray1OfShape1 {
    constructor();
  }

  export declare class Handle_StdPersistent_HArray1OfShape1_2 extends Handle_StdPersistent_HArray1OfShape1 {
    constructor(thePtr: StdPersistent_HArray1OfShape1);
  }

  export declare class Handle_StdPersistent_HArray1OfShape1_3 extends Handle_StdPersistent_HArray1OfShape1 {
    constructor(theHandle: Handle_StdPersistent_HArray1OfShape1);
  }

  export declare class Handle_StdPersistent_HArray1OfShape1_4 extends Handle_StdPersistent_HArray1OfShape1 {
    constructor(theHandle: Handle_StdPersistent_HArray1OfShape1);
  }

export declare class Handle_StdStorage_Root {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdStorage_Root): void;
  get(): StdStorage_Root;
  delete(): void;
}

  export declare class Handle_StdStorage_Root_1 extends Handle_StdStorage_Root {
    constructor();
  }

  export declare class Handle_StdStorage_Root_2 extends Handle_StdStorage_Root {
    constructor(thePtr: StdStorage_Root);
  }

  export declare class Handle_StdStorage_Root_3 extends Handle_StdStorage_Root {
    constructor(theHandle: Handle_StdStorage_Root);
  }

  export declare class Handle_StdStorage_Root_4 extends Handle_StdStorage_Root {
    constructor(theHandle: Handle_StdStorage_Root);
  }

export declare class Handle_StdStorage_HSequenceOfRoots {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdStorage_HSequenceOfRoots): void;
  get(): StdStorage_HSequenceOfRoots;
  delete(): void;
}

  export declare class Handle_StdStorage_HSequenceOfRoots_1 extends Handle_StdStorage_HSequenceOfRoots {
    constructor();
  }

  export declare class Handle_StdStorage_HSequenceOfRoots_2 extends Handle_StdStorage_HSequenceOfRoots {
    constructor(thePtr: StdStorage_HSequenceOfRoots);
  }

  export declare class Handle_StdStorage_HSequenceOfRoots_3 extends Handle_StdStorage_HSequenceOfRoots {
    constructor(theHandle: Handle_StdStorage_HSequenceOfRoots);
  }

  export declare class Handle_StdStorage_HSequenceOfRoots_4 extends Handle_StdStorage_HSequenceOfRoots {
    constructor(theHandle: Handle_StdStorage_HSequenceOfRoots);
  }

export declare class Handle_StdStorage_HeaderData {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdStorage_HeaderData): void;
  get(): StdStorage_HeaderData;
  delete(): void;
}

  export declare class Handle_StdStorage_HeaderData_1 extends Handle_StdStorage_HeaderData {
    constructor();
  }

  export declare class Handle_StdStorage_HeaderData_2 extends Handle_StdStorage_HeaderData {
    constructor(thePtr: StdStorage_HeaderData);
  }

  export declare class Handle_StdStorage_HeaderData_3 extends Handle_StdStorage_HeaderData {
    constructor(theHandle: Handle_StdStorage_HeaderData);
  }

  export declare class Handle_StdStorage_HeaderData_4 extends Handle_StdStorage_HeaderData {
    constructor(theHandle: Handle_StdStorage_HeaderData);
  }

export declare class Handle_StdStorage_RootData {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdStorage_RootData): void;
  get(): StdStorage_RootData;
  delete(): void;
}

  export declare class Handle_StdStorage_RootData_1 extends Handle_StdStorage_RootData {
    constructor();
  }

  export declare class Handle_StdStorage_RootData_2 extends Handle_StdStorage_RootData {
    constructor(thePtr: StdStorage_RootData);
  }

  export declare class Handle_StdStorage_RootData_3 extends Handle_StdStorage_RootData {
    constructor(theHandle: Handle_StdStorage_RootData);
  }

  export declare class Handle_StdStorage_RootData_4 extends Handle_StdStorage_RootData {
    constructor(theHandle: Handle_StdStorage_RootData);
  }

export declare class Handle_StdStorage_TypeData {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdStorage_TypeData): void;
  get(): StdStorage_TypeData;
  delete(): void;
}

  export declare class Handle_StdStorage_TypeData_1 extends Handle_StdStorage_TypeData {
    constructor();
  }

  export declare class Handle_StdStorage_TypeData_2 extends Handle_StdStorage_TypeData {
    constructor(thePtr: StdStorage_TypeData);
  }

  export declare class Handle_StdStorage_TypeData_3 extends Handle_StdStorage_TypeData {
    constructor(theHandle: Handle_StdStorage_TypeData);
  }

  export declare class Handle_StdStorage_TypeData_4 extends Handle_StdStorage_TypeData {
    constructor(theHandle: Handle_StdStorage_TypeData);
  }

export declare type ShapePersistent_TriangleMode = {
  ShapePersistent_WithTriangle: {};
  ShapePersistent_WithoutTriangle: {};
}

export declare type module_TKStd_wasm = {
  ShapePersistent: typeof ShapePersistent;
  StdPersistent_TopoDS: typeof StdPersistent_TopoDS;
  StdObject_Location: typeof StdObject_Location;
  StdObject_Shape: typeof StdObject_Shape;
  StdPersistent_HArray1: typeof StdPersistent_HArray1;
  ShapePersistent_HArray1: typeof ShapePersistent_HArray1;
  ShapePersistent_HArray2: typeof ShapePersistent_HArray2;
  ShapePersistent_HSequence: typeof ShapePersistent_HSequence;
  StdDrivers: typeof StdDrivers;
  StdDrivers_DocumentRetrievalDriver: typeof StdDrivers_DocumentRetrievalDriver;
  StdPersistent: typeof StdPersistent;
  StdPersistent_DataXtd: typeof StdPersistent_DataXtd;
  StdPersistent_DataXtd_Constraint: typeof StdPersistent_DataXtd_Constraint;
  StdPersistent_DataXtd_PatternStd: typeof StdPersistent_DataXtd_PatternStd;
  StdPersistent_Naming: typeof StdPersistent_Naming;
  StdPersistent_PPrsStd: typeof StdPersistent_PPrsStd;
  StdStorage: typeof StdStorage;
  StdStorage_Bucket: typeof StdStorage_Bucket;
  StdStorage_Bucket_1: typeof StdStorage_Bucket_1;
  StdStorage_Bucket_2: typeof StdStorage_Bucket_2;
  StdStorage_BucketOfPersistent: typeof StdStorage_BucketOfPersistent;
  StdStorage_BucketIterator: typeof StdStorage_BucketIterator;
  StdStorage_Data: typeof StdStorage_Data;
  StdStorage_Root: typeof StdStorage_Root;
  StdStorage_Root_1: typeof StdStorage_Root_1;
  StdStorage_Root_2: typeof StdStorage_Root_2;
  StdStorage_HeaderData: typeof StdStorage_HeaderData;
  StdStorage_RootData: typeof StdStorage_RootData;
  StdStorage_TypeData: typeof StdStorage_TypeData;
  handle: typeof handle;
  Handle_StdPersistent_HArray1OfShape1_1: typeof Handle_StdPersistent_HArray1OfShape1_1;
  Handle_StdPersistent_HArray1OfShape1_2: typeof Handle_StdPersistent_HArray1OfShape1_2;
  Handle_StdPersistent_HArray1OfShape1_3: typeof Handle_StdPersistent_HArray1OfShape1_3;
  Handle_StdPersistent_HArray1OfShape1_4: typeof Handle_StdPersistent_HArray1OfShape1_4;
  handle: typeof handle;
  Handle_StdStorage_Root_1: typeof Handle_StdStorage_Root_1;
  Handle_StdStorage_Root_2: typeof Handle_StdStorage_Root_2;
  Handle_StdStorage_Root_3: typeof Handle_StdStorage_Root_3;
  Handle_StdStorage_Root_4: typeof Handle_StdStorage_Root_4;
  handle: typeof handle;
  Handle_StdStorage_HSequenceOfRoots_1: typeof Handle_StdStorage_HSequenceOfRoots_1;
  Handle_StdStorage_HSequenceOfRoots_2: typeof Handle_StdStorage_HSequenceOfRoots_2;
  Handle_StdStorage_HSequenceOfRoots_3: typeof Handle_StdStorage_HSequenceOfRoots_3;
  Handle_StdStorage_HSequenceOfRoots_4: typeof Handle_StdStorage_HSequenceOfRoots_4;
  handle: typeof handle;
  Handle_StdStorage_HeaderData_1: typeof Handle_StdStorage_HeaderData_1;
  Handle_StdStorage_HeaderData_2: typeof Handle_StdStorage_HeaderData_2;
  Handle_StdStorage_HeaderData_3: typeof Handle_StdStorage_HeaderData_3;
  Handle_StdStorage_HeaderData_4: typeof Handle_StdStorage_HeaderData_4;
  handle: typeof handle;
  Handle_StdStorage_RootData_1: typeof Handle_StdStorage_RootData_1;
  Handle_StdStorage_RootData_2: typeof Handle_StdStorage_RootData_2;
  Handle_StdStorage_RootData_3: typeof Handle_StdStorage_RootData_3;
  Handle_StdStorage_RootData_4: typeof Handle_StdStorage_RootData_4;
  handle: typeof handle;
  Handle_StdStorage_TypeData_1: typeof Handle_StdStorage_TypeData_1;
  Handle_StdStorage_TypeData_2: typeof Handle_StdStorage_TypeData_2;
  Handle_StdStorage_TypeData_3: typeof Handle_StdStorage_TypeData_3;
  Handle_StdStorage_TypeData_4: typeof Handle_StdStorage_TypeData_4;
  ShapePersistent_TriangleMode: typeof ShapePersistent_TriangleMode;
};
