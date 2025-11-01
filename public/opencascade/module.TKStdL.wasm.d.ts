declare const libName = "./module.TKStdL.wasm.d.ts";
export default libName;

type Standard_Boolean = boolean;
type Standard_Byte = number;
type Standard_Character = number;
type Standard_CString = string;
type Standard_Integer = number;
type Standard_Real = number;
type Standard_ShortReal = number;
type Standard_Size = number;

export declare class StdObjMgt_Persistent extends Standard_Transient {
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  ImportDocument(theDocument: any): void;
  CreateAttribute(): any;
  GetAttribute(): any;
  ImportAttribute(): void;
  AsciiString(): any;
  ExtString(): any;
  Label(theDF: any): TDF_Label;
  TypeNum_1(): Standard_Integer;
  TypeNum_2(theTypeNum: Standard_Integer): void;
  RefNum_1(): Standard_Integer;
  RefNum_2(theRefNum: Standard_Integer): void;
  delete(): void;
}

export declare class StdObjMgt_SharedObject {
  constructor();
  delete(): void;
}

export declare class StdObjMgt_ReadData {
  constructor(theDriver: any, theNumberOfObjects: Standard_Integer)
  ReadPersistentObject(theRef: Standard_Integer): void;
  PersistentObject(theRef: Standard_Integer): any;
  ReadReference(): any;
  delete(): void;
}

export declare class StdObjMgt_WriteData {
  constructor(theDriver: any)
  WritePersistentObject(thePersistent: any): void;
  delete(): void;
}

export declare class StdLPersistent_HArray1 {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_HArray2 {
  constructor();
  delete(): void;
}

export declare class StdLDrivers_DocumentRetrievalDriver extends PCDM_RetrievalDriver {
  constructor();
  CreateDocument(): any;
  Read_1(theFileName: TCollection_ExtendedString, theNewDocument: any, theApplication: any, theRange: Message_ProgressRange): void;
  Read_2(theIStream: Standard_IStream, theStorageData: any, theDoc: any, theApplication: any, theRange: Message_ProgressRange): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class StdLDrivers {
  constructor();
  static Factory(aGUID: Standard_GUID): any;
  static DefineFormat(theApp: any): void;
  static BindTypes(theMap: StdObjMgt_MapOfInstantiators): void;
  delete(): void;
}

export declare class StdLPersistent {
  constructor();
  static BindTypes(theMap: StdObjMgt_MapOfInstantiators): void;
  delete(): void;
}

export declare class StdLPersistent_Collection {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_Data extends StdObjMgt_Persistent {
  constructor()
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(theChildren: any): void;
  PName(): Standard_CString;
  Import(): any;
  delete(): void;
}

export declare class StdLPersistent_HString {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_Dependency {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_Document extends StdObjMgt_Persistent {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  ImportDocument(theDocument: any): void;
  delete(): void;
}

export declare class StdLPersistent_Function {
  constructor()
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdLPersistent_NamedData {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdLPersistent_Real {
  constructor()
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdLPersistent_TreeNode {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(a0: any): void;
  PName(): Standard_CString;
  CreateAttribute(): any;
  ImportAttribute(): void;
  delete(): void;
}

export declare class StdLPersistent_Value {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_Variable {
  constructor()
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(theChildren: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdLPersistent_Void {
  constructor();
  delete(): void;
}

export declare class StdLPersistent_XLink {
  constructor();
  Read(theReadData: StdObjMgt_ReadData): void;
  Write(theWriteData: StdObjMgt_WriteData): void;
  PChildren(theChildren: any): void;
  PName(): Standard_CString;
  Import(theAttribute: any): void;
  delete(): void;
}

export declare class StdObjMgt_MapOfInstantiators {
  constructor();
  delete(): void;
}

export declare class Handle_StdLPersistent_HArray1OfPersistent {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdLPersistent_HArray1OfPersistent): void;
  get(): StdLPersistent_HArray1OfPersistent;
  delete(): void;
}

  export declare class Handle_StdLPersistent_HArray1OfPersistent_1 extends Handle_StdLPersistent_HArray1OfPersistent {
    constructor();
  }

  export declare class Handle_StdLPersistent_HArray1OfPersistent_2 extends Handle_StdLPersistent_HArray1OfPersistent {
    constructor(thePtr: StdLPersistent_HArray1OfPersistent);
  }

  export declare class Handle_StdLPersistent_HArray1OfPersistent_3 extends Handle_StdLPersistent_HArray1OfPersistent {
    constructor(theHandle: Handle_StdLPersistent_HArray1OfPersistent);
  }

  export declare class Handle_StdLPersistent_HArray1OfPersistent_4 extends Handle_StdLPersistent_HArray1OfPersistent {
    constructor(theHandle: Handle_StdLPersistent_HArray1OfPersistent);
  }

export declare class Handle_StdLPersistent_HArray2OfPersistent {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: StdLPersistent_HArray2OfPersistent): void;
  get(): StdLPersistent_HArray2OfPersistent;
  delete(): void;
}

  export declare class Handle_StdLPersistent_HArray2OfPersistent_1 extends Handle_StdLPersistent_HArray2OfPersistent {
    constructor();
  }

  export declare class Handle_StdLPersistent_HArray2OfPersistent_2 extends Handle_StdLPersistent_HArray2OfPersistent {
    constructor(thePtr: StdLPersistent_HArray2OfPersistent);
  }

  export declare class Handle_StdLPersistent_HArray2OfPersistent_3 extends Handle_StdLPersistent_HArray2OfPersistent {
    constructor(theHandle: Handle_StdLPersistent_HArray2OfPersistent);
  }

  export declare class Handle_StdLPersistent_HArray2OfPersistent_4 extends Handle_StdLPersistent_HArray2OfPersistent {
    constructor(theHandle: Handle_StdLPersistent_HArray2OfPersistent);
  }

export declare type module_TKStdL_wasm = {
  StdObjMgt_Persistent: typeof StdObjMgt_Persistent;
  StdObjMgt_SharedObject: typeof StdObjMgt_SharedObject;
  StdObjMgt_ReadData: typeof StdObjMgt_ReadData;
  StdObjMgt_WriteData: typeof StdObjMgt_WriteData;
  StdLPersistent_HArray1: typeof StdLPersistent_HArray1;
  StdLPersistent_HArray2: typeof StdLPersistent_HArray2;
  StdLDrivers_DocumentRetrievalDriver: typeof StdLDrivers_DocumentRetrievalDriver;
  StdLDrivers: typeof StdLDrivers;
  StdLPersistent: typeof StdLPersistent;
  StdLPersistent_Collection: typeof StdLPersistent_Collection;
  StdLPersistent_Data: typeof StdLPersistent_Data;
  StdLPersistent_HString: typeof StdLPersistent_HString;
  StdLPersistent_Dependency: typeof StdLPersistent_Dependency;
  StdLPersistent_Document: typeof StdLPersistent_Document;
  StdLPersistent_Function: typeof StdLPersistent_Function;
  StdLPersistent_NamedData: typeof StdLPersistent_NamedData;
  StdLPersistent_Real: typeof StdLPersistent_Real;
  StdLPersistent_TreeNode: typeof StdLPersistent_TreeNode;
  StdLPersistent_Value: typeof StdLPersistent_Value;
  StdLPersistent_Variable: typeof StdLPersistent_Variable;
  StdLPersistent_Void: typeof StdLPersistent_Void;
  StdLPersistent_XLink: typeof StdLPersistent_XLink;
  StdObjMgt_MapOfInstantiators: typeof StdObjMgt_MapOfInstantiators;
  handle: typeof handle;
  Handle_StdLPersistent_HArray1OfPersistent_1: typeof Handle_StdLPersistent_HArray1OfPersistent_1;
  Handle_StdLPersistent_HArray1OfPersistent_2: typeof Handle_StdLPersistent_HArray1OfPersistent_2;
  Handle_StdLPersistent_HArray1OfPersistent_3: typeof Handle_StdLPersistent_HArray1OfPersistent_3;
  Handle_StdLPersistent_HArray1OfPersistent_4: typeof Handle_StdLPersistent_HArray1OfPersistent_4;
  handle: typeof handle;
  Handle_StdLPersistent_HArray2OfPersistent_1: typeof Handle_StdLPersistent_HArray2OfPersistent_1;
  Handle_StdLPersistent_HArray2OfPersistent_2: typeof Handle_StdLPersistent_HArray2OfPersistent_2;
  Handle_StdLPersistent_HArray2OfPersistent_3: typeof Handle_StdLPersistent_HArray2OfPersistent_3;
  Handle_StdLPersistent_HArray2OfPersistent_4: typeof Handle_StdLPersistent_HArray2OfPersistent_4;
};
