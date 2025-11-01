declare const libName = "./module.TKCDF.wasm.d.ts";
export default libName;

type Standard_Boolean = boolean;
type Standard_Byte = number;
type Standard_Character = number;
type Standard_CString = string;
type Standard_Integer = number;
type Standard_Real = number;
type Standard_ShortReal = number;
type Standard_Size = number;

export declare class CDF_MetaDataDriver extends Standard_Transient {
  HasVersionCapability(): Standard_Boolean;
  CreateDependsOn(aFirstData: any, aSecondData: any): void;
  CreateReference(aFrom: any, aTo: any, aReferenceIdentifier: Standard_Integer, aToDocumentVersion: Standard_Integer): void;
  HasVersion(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString): Standard_Boolean;
  BuildFileName(aDocument: any): TCollection_ExtendedString;
  SetName(aDocument: any, aName: TCollection_ExtendedString): TCollection_ExtendedString;
  Find_1(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): Standard_Boolean;
  HasReadPermission(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): Standard_Boolean;
  MetaData_1(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): any;
  LastVersion(aMetaData: any): any;
  CreateMetaData(aDocument: any, aFileName: TCollection_ExtendedString): any;
  FindFolder(aFolder: TCollection_ExtendedString): Standard_Boolean;
  DefaultFolder(): TCollection_ExtendedString;
  ReferenceIterator(theMessageDriver: any): any;
  Find_2(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString): Standard_Boolean;
  MetaData_2(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDM_Application extends Standard_Transient {
  Resources(): any;
  MessageDriver(): any;
  BeginOfUpdate(aDocument: any): void;
  EndOfUpdate(aDocument: any, theStatus: Standard_Boolean, ErrorString: TCollection_ExtendedString): void;
  Write(aString: Standard_ExtString): void;
  Name(): TCollection_ExtendedString;
  Version(): TCollection_AsciiString;
  MetaDataLookUpTable(): CDM_MetaDataLookUpTable;
  DumpJson(theOStream: Standard_OStream, theDepth: Standard_Integer): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDF_Application extends CDM_Application {
  static Load(aGUID: Standard_GUID): any;
  Open(aDocument: any): void;
  CanClose(aDocument: any): CDM_CanCloseStatus;
  Close(aDocument: any): void;
  Retrieve_1(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, UseStorageConfiguration: Standard_Boolean, theRange: Message_ProgressRange): any;
  Retrieve_2(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString, UseStorageConfiguration: Standard_Boolean, theRange: Message_ProgressRange): any;
  CanRetrieve_1(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString): PCDM_ReaderStatus;
  CanRetrieve_2(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): PCDM_ReaderStatus;
  GetRetrieveStatus(): PCDM_ReaderStatus;
  Read(theIStream: Standard_IStream, theRange: Message_ProgressRange): any;
  ReaderFromFormat(aFormat: TCollection_ExtendedString): any;
  WriterFromFormat(aFormat: TCollection_ExtendedString): any;
  Format(aFileName: TCollection_ExtendedString, theFormat: TCollection_ExtendedString): Standard_Boolean;
  DefaultFolder(): Standard_ExtString;
  SetDefaultFolder(aFolder: Standard_ExtString): Standard_Boolean;
  MetaDataDriver(): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_Reader extends Standard_Transient {
  CreateDocument(): any;
  Read_1(aFileName: TCollection_ExtendedString, aNewDocument: any, anApplication: any, theProgress: Message_ProgressRange): void;
  Read_2(theIStream: Standard_IStream, theStorageData: any, theDoc: any, theApplication: any, theProgress: Message_ProgressRange): void;
  GetStatus(): PCDM_ReaderStatus;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_Reference {
  ReferenceIdentifier(): Standard_Integer;
  FileName(): TCollection_ExtendedString;
  DocumentVersion(): Standard_Integer;
  delete(): void;
}

  export declare class PCDM_Reference_1 extends PCDM_Reference {
    constructor();
  }

  export declare class PCDM_Reference_2 extends PCDM_Reference {
    constructor(aReferenceIdentifier: Standard_Integer, aFileName: TCollection_ExtendedString, aDocumentVersion: Standard_Integer);
  }

export declare class PCDM_ReferenceIterator extends Standard_Transient {
  constructor(theMessageDriver: any)
  LoadReferences(aDocument: any, aMetaData: any, anApplication: any, UseStorageConfiguration: Standard_Boolean): void;
  Init(aMetaData: any): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_RetrievalDriver extends PCDM_Reader {
  static DocumentVersion(theFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  static ReferenceCounter(theFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  SetFormat(aformat: TCollection_ExtendedString): void;
  GetFormat(): TCollection_ExtendedString;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_Writer extends Standard_Transient {
  Write_1(aDocument: any, aFileName: TCollection_ExtendedString, theRange: Message_ProgressRange): void;
  Write_2(theDocument: any, theOStream: Standard_OStream, theRange: Message_ProgressRange): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_Document extends Standard_Persistent {
  constructor();
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_StorageDriver extends PCDM_Writer {
  constructor();
  Make_1(aDocument: any): any;
  Make_2(aDocument: any, Documents: PCDM_SequenceOfDocument): void;
  Write_1(aDocument: any, aFileName: TCollection_ExtendedString, theRange: Message_ProgressRange): void;
  Write_2(theDocument: any, theOStream: Standard_OStream, theRange: Message_ProgressRange): void;
  SetFormat(aformat: TCollection_ExtendedString): void;
  GetFormat(): TCollection_ExtendedString;
  IsError(): Standard_Boolean;
  SetIsError(theIsError: Standard_Boolean): void;
  GetStoreStatus(): PCDM_StoreStatus;
  SetStoreStatus(theStoreStatus: PCDM_StoreStatus): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDM_Reference extends Standard_Transient {
  FromDocument(): any;
  ToDocument(): any;
  ReferenceIdentifier(): Standard_Integer;
  DocumentVersion(): Standard_Integer;
  IsReadOnly(): Standard_Boolean;
  DumpJson(theOStream: Standard_OStream, theDepth: Standard_Integer): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDM_Document extends Standard_Transient {
  Update_1(aToDocument: any, aReferenceIdentifier: Standard_Integer, aModifContext: Standard_Address): void;
  Update_2(ErrorString: TCollection_ExtendedString): Standard_Boolean;
  StorageFormat(): TCollection_ExtendedString;
  Extensions(Extensions: TColStd_SequenceOfExtendedString): void;
  GetAlternativeDocument(aFormat: TCollection_ExtendedString, anAlternativeDocument: any): Standard_Boolean;
  CreateReference_1(anOtherDocument: any): Standard_Integer;
  RemoveReference(aReferenceIdentifier: Standard_Integer): void;
  RemoveAllReferences(): void;
  Document(aReferenceIdentifier: Standard_Integer): any;
  IsInSession(aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  IsStored_1(aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  Name(aReferenceIdentifier: Standard_Integer): TCollection_ExtendedString;
  UpdateFromDocuments(aModifContext: Standard_Address): void;
  ToReferencesNumber(): Standard_Integer;
  FromReferencesNumber(): Standard_Integer;
  ShallowReferences(aDocument: any): Standard_Boolean;
  DeepReferences(aDocument: any): Standard_Boolean;
  CopyReference(aFromDocument: any, aReferenceIdentifier: Standard_Integer): Standard_Integer;
  IsReadOnly_1(): Standard_Boolean;
  IsReadOnly_2(aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  SetIsReadOnly(): void;
  UnsetIsReadOnly(): void;
  Modify(): void;
  Modifications(): Standard_Integer;
  UnModify(): void;
  IsUpToDate(aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  SetIsUpToDate(aReferenceIdentifier: Standard_Integer): void;
  SetComment(aComment: TCollection_ExtendedString): void;
  AddComment(aComment: TCollection_ExtendedString): void;
  SetComments(aComments: TColStd_SequenceOfExtendedString): void;
  Comments(aComments: TColStd_SequenceOfExtendedString): void;
  Comment(): Standard_ExtString;
  IsStored_2(): Standard_Boolean;
  StorageVersion(): Standard_Integer;
  SetMetaData(aMetaData: any): void;
  UnsetIsStored(): void;
  MetaData(): any;
  Folder(): TCollection_ExtendedString;
  SetRequestedFolder(aFolder: TCollection_ExtendedString): void;
  RequestedFolder(): TCollection_ExtendedString;
  HasRequestedFolder(): Standard_Boolean;
  SetRequestedName(aName: TCollection_ExtendedString): void;
  RequestedName(): TCollection_ExtendedString;
  SetRequestedPreviousVersion(aPreviousVersion: TCollection_ExtendedString): void;
  UnsetRequestedPreviousVersion(): void;
  HasRequestedPreviousVersion(): Standard_Boolean;
  RequestedPreviousVersion(): TCollection_ExtendedString;
  SetRequestedComment(aComment: TCollection_ExtendedString): void;
  RequestedComment(): TCollection_ExtendedString;
  LoadResources(): void;
  FindFileExtension(): Standard_Boolean;
  FileExtension(): TCollection_ExtendedString;
  FindDescription(): Standard_Boolean;
  Description(): TCollection_ExtendedString;
  IsModified(): Standard_Boolean;
  IsOpened_1(): Standard_Boolean;
  Open(anApplication: any): void;
  CanClose(): CDM_CanCloseStatus;
  Close(): void;
  Application(): any;
  CanCloseReference(aDocument: any, aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  CloseReference(aDocument: any, aReferenceIdentifier: Standard_Integer): void;
  IsOpened_2(aReferenceIdentifier: Standard_Integer): Standard_Boolean;
  CreateReference_2(aMetaData: any, aReferenceIdentifier: Standard_Integer, anApplication: any, aToDocumentVersion: Standard_Integer, UseStorageConfiguration: Standard_Boolean): void;
  CreateReference_3(aMetaData: any, anApplication: any, aDocumentVersion: Standard_Integer, UseStorageConfiguration: Standard_Boolean): Standard_Integer;
  ReferenceCounter(): Standard_Integer;
  Update_3(): void;
  Reference(aReferenceIdentifier: Standard_Integer): any;
  SetModifications(Modifications: Standard_Integer): void;
  SetReferenceCounter(aReferenceCounter: Standard_Integer): void;
  StorageFormatVersion(): Standard_Integer;
  ChangeStorageFormatVersion(theVersion: Standard_Integer): void;
  DumpJson(theOStream: Standard_OStream, theDepth: Standard_Integer): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDF_Directory extends Standard_Transient {
  constructor()
  Add(aDocument: any): void;
  Remove(aDocument: any): void;
  Contains(aDocument: any): Standard_Boolean;
  Last(): any;
  Length(): Standard_Integer;
  IsEmpty(): Standard_Boolean;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDF_FWOSDriver extends CDF_MetaDataDriver {
  constructor(theLookUpTable: CDM_MetaDataLookUpTable)
  Find(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): Standard_Boolean;
  HasReadPermission(aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aVersion: TCollection_ExtendedString): Standard_Boolean;
  FindFolder(aFolder: TCollection_ExtendedString): Standard_Boolean;
  DefaultFolder(): TCollection_ExtendedString;
  BuildFileName(aDocument: any): TCollection_ExtendedString;
  SetName(aDocument: any, aName: TCollection_ExtendedString): TCollection_ExtendedString;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDF_MetaDataDriverError extends Standard_Failure {
  static Raise_1(theMessage: Standard_CString): void;
  static Raise_2(theMessage: Standard_SStream): void;
  static NewInstance(theMessage: Standard_CString): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

  export declare class CDF_MetaDataDriverError_1 extends CDF_MetaDataDriverError {
    constructor();
  }

  export declare class CDF_MetaDataDriverError_2 extends CDF_MetaDataDriverError {
    constructor(theMessage: Standard_CString);
  }

export declare class CDF_MetaDataDriverFactory extends Standard_Transient {
  Build(): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDF_Store {
  constructor(aDocument: any)
  Folder(): any;
  Name(): any;
  IsStored(): Standard_Boolean;
  IsModified(): Standard_Boolean;
  CurrentIsConsistent(): Standard_Boolean;
  IsConsistent(): Standard_Boolean;
  HasAPreviousVersion(): Standard_Boolean;
  PreviousVersion(): any;
  IsMainDocument(): Standard_Boolean;
  SetFolder_1(aFolder: TCollection_ExtendedString): Standard_Boolean;
  SetName_1(aName: Standard_ExtString): CDF_StoreSetNameStatus;
  SetComment(aComment: Standard_ExtString): void;
  Comment(): any;
  RecheckName(): CDF_StoreSetNameStatus;
  SetPreviousVersion(aPreviousVersion: Standard_ExtString): Standard_Boolean;
  Realize(theRange: Message_ProgressRange): void;
  Path(): Standard_ExtString;
  MetaDataPath(): any;
  Description(): any;
  SetCurrent(aPresentation: Standard_ExtString): void;
  SetMain(): void;
  StoreStatus(): PCDM_StoreStatus;
  AssociatedStatusText(): Standard_ExtString;
  SetName_2(aName: TCollection_ExtendedString): CDF_StoreSetNameStatus;
  SetFolder_2(aFolder: Standard_ExtString): Standard_Boolean;
  delete(): void;
}

export declare class CDF_StoreList extends Standard_Transient {
  constructor(aDocument: any)
  IsConsistent(): Standard_Boolean;
  Store(aMetaData: any, aStatusAssociatedText: TCollection_ExtendedString, theRange: Message_ProgressRange): PCDM_StoreStatus;
  Init(): void;
  More(): Standard_Boolean;
  Next(): void;
  Value(): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDM_MetaData extends Standard_Transient {
  static LookUp_1(theLookUpTable: CDM_MetaDataLookUpTable, aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aPath: TCollection_ExtendedString, aFileName: TCollection_ExtendedString, ReadOnly: Standard_Boolean): any;
  static LookUp_2(theLookUpTable: CDM_MetaDataLookUpTable, aFolder: TCollection_ExtendedString, aName: TCollection_ExtendedString, aPath: TCollection_ExtendedString, aVersion: TCollection_ExtendedString, aFileName: TCollection_ExtendedString, ReadOnly: Standard_Boolean): any;
  IsRetrieved(): Standard_Boolean;
  Document(): any;
  Folder(): TCollection_ExtendedString;
  Name(): TCollection_ExtendedString;
  Version(): TCollection_ExtendedString;
  HasVersion(): Standard_Boolean;
  FileName(): TCollection_ExtendedString;
  Path(): TCollection_ExtendedString;
  UnsetDocument(): void;
  IsReadOnly(): Standard_Boolean;
  SetIsReadOnly(): void;
  UnsetIsReadOnly(): void;
  DumpJson(theOStream: Standard_OStream, theDepth: Standard_Integer): void;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class CDM_ReferenceIterator {
  constructor(aDocument: any)
  More(): Standard_Boolean;
  Next(): void;
  Document(): any;
  ReferenceIdentifier(): Standard_Integer;
  DocumentVersion(): Standard_Integer;
  delete(): void;
}

export declare class LDOMBasicString {
  Type(): any;
  GetInteger(aResult: Standard_Integer): Standard_Boolean;
  GetString(): string;
  equals(anOther: LDOMBasicString): Standard_Boolean;
  delete(): void;
}

  export declare class LDOMBasicString_1 extends LDOMBasicString {
    constructor();
  }

  export declare class LDOMBasicString_2 extends LDOMBasicString {
    constructor(anOther: LDOMBasicString);
  }

  export declare class LDOMBasicString_3 extends LDOMBasicString {
    constructor(aValue: Standard_Integer);
  }

  export declare class LDOMBasicString_4 extends LDOMBasicString {
    constructor(aValue: string);
  }

  export declare class LDOMBasicString_5 extends LDOMBasicString {
    constructor(aValue: string, aDoc: any);
  }

  export declare class LDOMBasicString_6 extends LDOMBasicString {
    constructor(aValue: string, aLen: Standard_Integer, aDoc: any);
  }

export declare class LDOMString extends LDOMBasicString {
  delete(): void;
}

  export declare class LDOMString_1 extends LDOMString {
    constructor();
  }

  export declare class LDOMString_2 extends LDOMString {
    constructor(anOther: LDOMString);
  }

  export declare class LDOMString_3 extends LDOMString {
    constructor(aValue: Standard_Integer);
  }

  export declare class LDOMString_4 extends LDOMString {
    constructor(aValue: string);
  }

export declare class LDOM_MemManager extends Standard_Transient {
  constructor(aBlockSize: Standard_Integer)
  Allocate(aSize: Standard_Integer): void;
  HashedAllocate_1(aString: string, theLen: Standard_Integer, theHash: Standard_Integer): string;
  HashedAllocate_2(aString: string, theLen: Standard_Integer, theResult: LDOMBasicString): void;
  static Hash(theString: string, theLen: Standard_Integer): Standard_Integer;
  static CompareStrings(theString: string, theHashValue: Standard_Integer, theHashedStr: string): Standard_Boolean;
  RootElement(): LDOM_BasicElement;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class LDOM_Node {
  isNull(): Standard_Boolean;
  getNodeType(): any;
  getNodeName(): LDOMString;
  getNodeValue(): LDOMString;
  getFirstChild(): LDOM_Node;
  getLastChild(): LDOM_Node;
  getNextSibling(): LDOM_Node;
  removeChild(aChild: LDOM_Node): void;
  appendChild(aChild: LDOM_Node): void;
  hasChildNodes(): Standard_Boolean;
  SetValueClear(): void;
  delete(): void;
}

  export declare class LDOM_Node_1 extends LDOM_Node {
    constructor();
  }

  export declare class LDOM_Node_2 extends LDOM_Node {
    constructor(anOther: LDOM_Node);
  }

export declare class LDOM_Attr extends LDOM_Node {
  getName(): LDOMString;
  getValue(): LDOMString;
  setValue(aValue: LDOMString): void;
  delete(): void;
}

  export declare class LDOM_Attr_1 extends LDOM_Attr {
    constructor();
  }

  export declare class LDOM_Attr_2 extends LDOM_Attr {
    constructor(anOther: LDOM_Attr);
  }

export declare class LDOM_NodeList {
  item(a0: Standard_Integer): LDOM_Node;
  getLength(): Standard_Integer;
  delete(): void;
}

  export declare class LDOM_NodeList_1 extends LDOM_NodeList {
    constructor();
  }

  export declare class LDOM_NodeList_2 extends LDOM_NodeList {
    constructor(theOther: LDOM_NodeList);
  }

export declare class LDOM_Element extends LDOM_Node {
  getTagName(): LDOMString;
  getAttribute(aName: LDOMString): LDOMString;
  getAttributeNode(aName: LDOMString): LDOM_Attr;
  getElementsByTagName(aName: LDOMString): LDOM_NodeList;
  setAttribute(aName: LDOMString, aValue: LDOMString): void;
  setAttributeNode(aNewAttr: LDOM_Attr): void;
  removeAttribute(aName: LDOMString): void;
  GetChildByTagName(aTagName: LDOMString): LDOM_Element;
  GetSiblingByTagName(): LDOM_Element;
  ReplaceElement(anOther: LDOM_Element): void;
  GetAttributesList(): LDOM_NodeList;
  delete(): void;
}

  export declare class LDOM_Element_1 extends LDOM_Element {
    constructor();
  }

  export declare class LDOM_Element_2 extends LDOM_Element {
    constructor(anOther: LDOM_Element);
  }

export declare class LDOM_CharacterData extends LDOM_Node {
  getData(): LDOMString;
  setData(aValue: LDOMString): void;
  getLength(): Standard_Integer;
  delete(): void;
}

  export declare class LDOM_CharacterData_1 extends LDOM_CharacterData {
    constructor();
  }

  export declare class LDOM_CharacterData_2 extends LDOM_CharacterData {
    constructor(theOther: LDOM_CharacterData);
  }

export declare class LDOM_Text extends LDOM_CharacterData {
  delete(): void;
}

  export declare class LDOM_Text_1 extends LDOM_Text {
    constructor();
  }

  export declare class LDOM_Text_2 extends LDOM_Text {
    constructor(anOther: LDOM_Text);
  }

export declare class LDOM_CDATASection extends LDOM_Text {
  delete(): void;
}

  export declare class LDOM_CDATASection_1 extends LDOM_CDATASection {
    constructor();
  }

  export declare class LDOM_CDATASection_2 extends LDOM_CDATASection {
    constructor(theOther: LDOM_CDATASection);
  }

export declare class LDOM_Comment extends LDOM_CharacterData {
  delete(): void;
}

  export declare class LDOM_Comment_1 extends LDOM_Comment {
    constructor();
  }

  export declare class LDOM_Comment_2 extends LDOM_Comment {
    constructor(theOther: LDOM_Comment);
  }

export declare class LDOM_Document {
  static createDocument(theQualifiedName: LDOMString): LDOM_Document;
  createElement(theTagName: LDOMString): LDOM_Element;
  createCDATASection(theData: LDOMString): LDOM_CDATASection;
  createComment(theData: LDOMString): LDOM_Comment;
  createTextNode(theData: LDOMString): LDOM_Text;
  getDocumentElement(): LDOM_Element;
  getElementsByTagName(theTagName: LDOMString): LDOM_NodeList;
  isNull(): Standard_Boolean;
  delete(): void;
}

  export declare class LDOM_Document_1 extends LDOM_Document {
    constructor();
  }

  export declare class LDOM_Document_2 extends LDOM_Document {
    constructor(aMemManager: LDOM_MemManager);
  }

export declare class LDOM_SBuffer {
  constructor(theMaxBuf: Standard_Integer)
  str(): Standard_CString;
  Length(): Standard_Integer;
  Clear(): void;
  overflow(c: number): number;
  underflow(): number;
  xsputn(s: string, n: any): any;
  delete(): void;
}

export declare class LDOM_OSStream extends Standard_OStream {
  constructor(theMaxBuf: Standard_Integer)
  str(): Standard_CString;
  Length(): Standard_Integer;
  Clear(): void;
  delete(): void;
}

export declare class LDOMParser {
  constructor()
  getDocument(): LDOM_Document;
  parse_1(aFileName: string): Standard_Boolean;
  parse_2(anInput: any, theTagPerStep: Standard_Boolean, theWithoutRoot: Standard_Boolean): Standard_Boolean;
  GetError(aData: TCollection_AsciiString): TCollection_AsciiString;
  GetBOM(): any;
  delete(): void;
}

export declare class LDOM_BasicNode {
  isNull(): Standard_Boolean;
  getNodeType(): any;
  GetSibling(): LDOM_BasicNode;
  delete(): void;
}

export declare class LDOM_BasicAttribute extends LDOM_BasicNode {
  constructor()
  GetName(): string;
  GetValue(): LDOMBasicString;
  SetValue(aValue: LDOMBasicString, aDoc: any): void;
  delete(): void;
}

export declare class LDOM_BasicElement extends LDOM_BasicNode {
  constructor()
  static Create(aName: string, aLength: Standard_Integer, aDoc: any): LDOM_BasicElement;
  GetTagName(): string;
  GetFirstChild(): LDOM_BasicNode;
  GetLastChild(): LDOM_BasicNode;
  GetAttribute(aName: LDOMBasicString, aLastCh: LDOM_BasicNode): LDOM_BasicAttribute;
  delete(): void;
}

export declare class LDOM_BasicText extends LDOM_BasicNode {
  constructor()
  GetData(): LDOMBasicString;
  SetData(aValue: LDOMBasicString, aDoc: any): void;
  delete(): void;
}

export declare class LDOM_CharReference {
  constructor();
  static Decode(theSrc: string, theLen: Standard_Integer): string;
  static Encode(theSrc: string, theLen: Standard_Integer, isAttribute: Standard_Boolean): string;
  delete(): void;
}

export declare class LDOM_DocumentType {
  constructor()
  delete(): void;
}

export declare class LDOM_LDOMImplementation {
  constructor();
  static createDocument(aNamespaceURI: LDOMString, aQualifiedName: LDOMString, aDocType: LDOM_DocumentType): LDOM_Document;
  delete(): void;
}

export declare class LDOM_XmlReader {
  constructor(aDocument: any, anErrorString: TCollection_AsciiString, theTagPerStep: Standard_Boolean)
  ReadRecord(theIStream: Standard_IStream, theData: LDOM_OSStream): any;
  GetElement(): LDOM_BasicElement;
  CreateElement(theName: string, theLen: Standard_Integer): void;
  static getInteger(theValue: LDOMBasicString, theStart: string, theEnd: string): Standard_Boolean;
  GetBOM(): any;
  delete(): void;
}

export declare class LDOM_XmlWriter {
  constructor(theEncoding: string)
  SetIndentation(theIndent: Standard_Integer): void;
  Write_1(theOStream: Standard_OStream, theDoc: LDOM_Document): void;
  Write_2(theOStream: Standard_OStream, theNode: LDOM_Node): void;
  delete(): void;
}

export declare class PCDM {
  constructor();
  static FileDriverType_1(aFileName: TCollection_AsciiString, aBaseDriver: any): PCDM_TypeOfFileDriver;
  static FileDriverType_2(theIStream: Standard_IStream, theBaseDriver: any): PCDM_TypeOfFileDriver;
  delete(): void;
}

export declare class PCDM_DOMHeaderParser extends LDOMParser {
  constructor();
  SetStartElementName(aStartElementName: TCollection_AsciiString): void;
  SetEndElementName(anEndElementName: TCollection_AsciiString): void;
  startElement(): Standard_Boolean;
  endElement(): Standard_Boolean;
  GetElement(): LDOM_Element;
  delete(): void;
}

export declare class PCDM_DriverError extends Standard_Failure {
  static Raise_1(theMessage: Standard_CString): void;
  static Raise_2(theMessage: Standard_SStream): void;
  static NewInstance(theMessage: Standard_CString): any;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

  export declare class PCDM_DriverError_1 extends PCDM_DriverError {
    constructor();
  }

  export declare class PCDM_DriverError_2 extends PCDM_DriverError {
    constructor(theMessage: Standard_CString);
  }

export declare class PCDM_ReadWriter extends Standard_Transient {
  Version(): TCollection_AsciiString;
  WriteReferenceCounter(aData: any, aDocument: any): void;
  WriteReferences(aData: any, aDocument: any, theReferencerFileName: TCollection_ExtendedString): void;
  WriteExtensions(aData: any, aDocument: any): void;
  WriteVersion(aData: any, aDocument: any): void;
  ReadReferenceCounter(theFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  ReadReferences(aFileName: TCollection_ExtendedString, theReferences: PCDM_SequenceOfReference, theMsgDriver: any): void;
  ReadExtensions(aFileName: TCollection_ExtendedString, theExtensions: TColStd_SequenceOfExtendedString, theMsgDriver: any): void;
  ReadDocumentVersion(aFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  static Open(aDriver: any, aFileName: TCollection_ExtendedString, anOpenMode: Storage_OpenMode): void;
  static Reader(aFileName: TCollection_ExtendedString): any;
  static Writer(): any;
  static WriteFileFormat(aData: any, aDocument: any): void;
  static FileFormat_1(aFileName: TCollection_ExtendedString): TCollection_ExtendedString;
  static FileFormat_2(theIStream: Standard_IStream, theData: any): TCollection_ExtendedString;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class PCDM_ReadWriter_1 extends PCDM_ReadWriter {
  constructor()
  Version(): TCollection_AsciiString;
  WriteReferenceCounter(aData: any, aDocument: any): void;
  WriteReferences(aData: any, aDocument: any, theReferencerFileName: TCollection_ExtendedString): void;
  WriteExtensions(aData: any, aDocument: any): void;
  WriteVersion(aData: any, aDocument: any): void;
  ReadReferenceCounter(aFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  ReadReferences(aFileName: TCollection_ExtendedString, theReferences: PCDM_SequenceOfReference, theMsgDriver: any): void;
  ReadExtensions(aFileName: TCollection_ExtendedString, theExtensions: TColStd_SequenceOfExtendedString, theMsgDriver: any): void;
  ReadDocumentVersion(aFileName: TCollection_ExtendedString, theMsgDriver: any): Standard_Integer;
  static get_type_name(): string;
  static get_type_descriptor(): any;
  DynamicType(): any;
  delete(): void;
}

export declare class Handle_CDF_MetaDataDriver {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_MetaDataDriver): void;
  get(): CDF_MetaDataDriver;
  delete(): void;
}

  export declare class Handle_CDF_MetaDataDriver_1 extends Handle_CDF_MetaDataDriver {
    constructor();
  }

  export declare class Handle_CDF_MetaDataDriver_2 extends Handle_CDF_MetaDataDriver {
    constructor(thePtr: CDF_MetaDataDriver);
  }

  export declare class Handle_CDF_MetaDataDriver_3 extends Handle_CDF_MetaDataDriver {
    constructor(theHandle: Handle_CDF_MetaDataDriver);
  }

  export declare class Handle_CDF_MetaDataDriver_4 extends Handle_CDF_MetaDataDriver {
    constructor(theHandle: Handle_CDF_MetaDataDriver);
  }

export declare class Handle_CDM_Application {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDM_Application): void;
  get(): CDM_Application;
  delete(): void;
}

  export declare class Handle_CDM_Application_1 extends Handle_CDM_Application {
    constructor();
  }

  export declare class Handle_CDM_Application_2 extends Handle_CDM_Application {
    constructor(thePtr: CDM_Application);
  }

  export declare class Handle_CDM_Application_3 extends Handle_CDM_Application {
    constructor(theHandle: Handle_CDM_Application);
  }

  export declare class Handle_CDM_Application_4 extends Handle_CDM_Application {
    constructor(theHandle: Handle_CDM_Application);
  }

export declare class Handle_CDF_Application {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_Application): void;
  get(): CDF_Application;
  delete(): void;
}

  export declare class Handle_CDF_Application_1 extends Handle_CDF_Application {
    constructor();
  }

  export declare class Handle_CDF_Application_2 extends Handle_CDF_Application {
    constructor(thePtr: CDF_Application);
  }

  export declare class Handle_CDF_Application_3 extends Handle_CDF_Application {
    constructor(theHandle: Handle_CDF_Application);
  }

  export declare class Handle_CDF_Application_4 extends Handle_CDF_Application {
    constructor(theHandle: Handle_CDF_Application);
  }

export declare class PCDM_SequenceOfReference extends NCollection_BaseSequence {
  begin(): any;
  end(): any;
  cbegin(): any;
  cend(): any;
  Size(): Standard_Integer;
  Length(): Standard_Integer;
  Lower(): Standard_Integer;
  Upper(): Standard_Integer;
  IsEmpty(): Standard_Boolean;
  Reverse(): void;
  Exchange(I: Standard_Integer, J: Standard_Integer): void;
  static delNode(theNode: NCollection_SeqNode, theAl: any): void;
  Clear(theAllocator: any): void;
  Assign(theOther: PCDM_SequenceOfReference): PCDM_SequenceOfReference;
  Remove_2(theIndex: Standard_Integer): void;
  Remove_3(theFromIndex: Standard_Integer, theToIndex: Standard_Integer): void;
  Append_1(theItem: PCDM_Reference): void;
  Append_2(theSeq: PCDM_SequenceOfReference): void;
  Prepend_1(theItem: PCDM_Reference): void;
  Prepend_2(theSeq: PCDM_SequenceOfReference): void;
  InsertBefore_1(theIndex: Standard_Integer, theItem: PCDM_Reference): void;
  InsertBefore_2(theIndex: Standard_Integer, theSeq: PCDM_SequenceOfReference): void;
  InsertAfter_2(theIndex: Standard_Integer, theSeq: PCDM_SequenceOfReference): void;
  InsertAfter_3(theIndex: Standard_Integer, theItem: PCDM_Reference): void;
  Split(theIndex: Standard_Integer, theSeq: PCDM_SequenceOfReference): void;
  First(): PCDM_Reference;
  ChangeFirst(): PCDM_Reference;
  Last(): PCDM_Reference;
  ChangeLast(): PCDM_Reference;
  Value(theIndex: Standard_Integer): PCDM_Reference;
  ChangeValue(theIndex: Standard_Integer): PCDM_Reference;
  SetValue(theIndex: Standard_Integer, theItem: PCDM_Reference): void;
  delete(): void;
}

  export declare class PCDM_SequenceOfReference_1 extends PCDM_SequenceOfReference {
    constructor();
  }

  export declare class PCDM_SequenceOfReference_2 extends PCDM_SequenceOfReference {
    constructor(theAllocator: any);
  }

  export declare class PCDM_SequenceOfReference_3 extends PCDM_SequenceOfReference {
    constructor(theOther: PCDM_SequenceOfReference);
  }

export declare class Handle_PCDM_ReferenceIterator {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_ReferenceIterator): void;
  get(): PCDM_ReferenceIterator;
  delete(): void;
}

  export declare class Handle_PCDM_ReferenceIterator_1 extends Handle_PCDM_ReferenceIterator {
    constructor();
  }

  export declare class Handle_PCDM_ReferenceIterator_2 extends Handle_PCDM_ReferenceIterator {
    constructor(thePtr: PCDM_ReferenceIterator);
  }

  export declare class Handle_PCDM_ReferenceIterator_3 extends Handle_PCDM_ReferenceIterator {
    constructor(theHandle: Handle_PCDM_ReferenceIterator);
  }

  export declare class Handle_PCDM_ReferenceIterator_4 extends Handle_PCDM_ReferenceIterator {
    constructor(theHandle: Handle_PCDM_ReferenceIterator);
  }

export declare class Handle_PCDM_RetrievalDriver {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_RetrievalDriver): void;
  get(): PCDM_RetrievalDriver;
  delete(): void;
}

  export declare class Handle_PCDM_RetrievalDriver_1 extends Handle_PCDM_RetrievalDriver {
    constructor();
  }

  export declare class Handle_PCDM_RetrievalDriver_2 extends Handle_PCDM_RetrievalDriver {
    constructor(thePtr: PCDM_RetrievalDriver);
  }

  export declare class Handle_PCDM_RetrievalDriver_3 extends Handle_PCDM_RetrievalDriver {
    constructor(theHandle: Handle_PCDM_RetrievalDriver);
  }

  export declare class Handle_PCDM_RetrievalDriver_4 extends Handle_PCDM_RetrievalDriver {
    constructor(theHandle: Handle_PCDM_RetrievalDriver);
  }

export declare class Handle_PCDM_Writer {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_Writer): void;
  get(): PCDM_Writer;
  delete(): void;
}

  export declare class Handle_PCDM_Writer_1 extends Handle_PCDM_Writer {
    constructor();
  }

  export declare class Handle_PCDM_Writer_2 extends Handle_PCDM_Writer {
    constructor(thePtr: PCDM_Writer);
  }

  export declare class Handle_PCDM_Writer_3 extends Handle_PCDM_Writer {
    constructor(theHandle: Handle_PCDM_Writer);
  }

  export declare class Handle_PCDM_Writer_4 extends Handle_PCDM_Writer {
    constructor(theHandle: Handle_PCDM_Writer);
  }

export declare class Handle_PCDM_Document {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_Document): void;
  get(): PCDM_Document;
  delete(): void;
}

  export declare class Handle_PCDM_Document_1 extends Handle_PCDM_Document {
    constructor();
  }

  export declare class Handle_PCDM_Document_2 extends Handle_PCDM_Document {
    constructor(thePtr: PCDM_Document);
  }

  export declare class Handle_PCDM_Document_3 extends Handle_PCDM_Document {
    constructor(theHandle: Handle_PCDM_Document);
  }

  export declare class Handle_PCDM_Document_4 extends Handle_PCDM_Document {
    constructor(theHandle: Handle_PCDM_Document);
  }

export declare class Handle_PCDM_StorageDriver {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_StorageDriver): void;
  get(): PCDM_StorageDriver;
  delete(): void;
}

  export declare class Handle_PCDM_StorageDriver_1 extends Handle_PCDM_StorageDriver {
    constructor();
  }

  export declare class Handle_PCDM_StorageDriver_2 extends Handle_PCDM_StorageDriver {
    constructor(thePtr: PCDM_StorageDriver);
  }

  export declare class Handle_PCDM_StorageDriver_3 extends Handle_PCDM_StorageDriver {
    constructor(theHandle: Handle_PCDM_StorageDriver);
  }

  export declare class Handle_PCDM_StorageDriver_4 extends Handle_PCDM_StorageDriver {
    constructor(theHandle: Handle_PCDM_StorageDriver);
  }

export declare class Handle_CDM_Reference {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDM_Reference): void;
  get(): CDM_Reference;
  delete(): void;
}

  export declare class Handle_CDM_Reference_1 extends Handle_CDM_Reference {
    constructor();
  }

  export declare class Handle_CDM_Reference_2 extends Handle_CDM_Reference {
    constructor(thePtr: CDM_Reference);
  }

  export declare class Handle_CDM_Reference_3 extends Handle_CDM_Reference {
    constructor(theHandle: Handle_CDM_Reference);
  }

  export declare class Handle_CDM_Reference_4 extends Handle_CDM_Reference {
    constructor(theHandle: Handle_CDM_Reference);
  }

export declare class Handle_CDM_Document {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDM_Document): void;
  get(): CDM_Document;
  delete(): void;
}

  export declare class Handle_CDM_Document_1 extends Handle_CDM_Document {
    constructor();
  }

  export declare class Handle_CDM_Document_2 extends Handle_CDM_Document {
    constructor(thePtr: CDM_Document);
  }

  export declare class Handle_CDM_Document_3 extends Handle_CDM_Document {
    constructor(theHandle: Handle_CDM_Document);
  }

  export declare class Handle_CDM_Document_4 extends Handle_CDM_Document {
    constructor(theHandle: Handle_CDM_Document);
  }

export declare class Handle_CDF_Directory {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_Directory): void;
  get(): CDF_Directory;
  delete(): void;
}

  export declare class Handle_CDF_Directory_1 extends Handle_CDF_Directory {
    constructor();
  }

  export declare class Handle_CDF_Directory_2 extends Handle_CDF_Directory {
    constructor(thePtr: CDF_Directory);
  }

  export declare class Handle_CDF_Directory_3 extends Handle_CDF_Directory {
    constructor(theHandle: Handle_CDF_Directory);
  }

  export declare class Handle_CDF_Directory_4 extends Handle_CDF_Directory {
    constructor(theHandle: Handle_CDF_Directory);
  }

export declare class Handle_CDF_FWOSDriver {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_FWOSDriver): void;
  get(): CDF_FWOSDriver;
  delete(): void;
}

  export declare class Handle_CDF_FWOSDriver_1 extends Handle_CDF_FWOSDriver {
    constructor();
  }

  export declare class Handle_CDF_FWOSDriver_2 extends Handle_CDF_FWOSDriver {
    constructor(thePtr: CDF_FWOSDriver);
  }

  export declare class Handle_CDF_FWOSDriver_3 extends Handle_CDF_FWOSDriver {
    constructor(theHandle: Handle_CDF_FWOSDriver);
  }

  export declare class Handle_CDF_FWOSDriver_4 extends Handle_CDF_FWOSDriver {
    constructor(theHandle: Handle_CDF_FWOSDriver);
  }

export declare class Handle_CDF_MetaDataDriverError {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_MetaDataDriverError): void;
  get(): CDF_MetaDataDriverError;
  delete(): void;
}

  export declare class Handle_CDF_MetaDataDriverError_1 extends Handle_CDF_MetaDataDriverError {
    constructor();
  }

  export declare class Handle_CDF_MetaDataDriverError_2 extends Handle_CDF_MetaDataDriverError {
    constructor(thePtr: CDF_MetaDataDriverError);
  }

  export declare class Handle_CDF_MetaDataDriverError_3 extends Handle_CDF_MetaDataDriverError {
    constructor(theHandle: Handle_CDF_MetaDataDriverError);
  }

  export declare class Handle_CDF_MetaDataDriverError_4 extends Handle_CDF_MetaDataDriverError {
    constructor(theHandle: Handle_CDF_MetaDataDriverError);
  }

export declare class Handle_CDF_MetaDataDriverFactory {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_MetaDataDriverFactory): void;
  get(): CDF_MetaDataDriverFactory;
  delete(): void;
}

  export declare class Handle_CDF_MetaDataDriverFactory_1 extends Handle_CDF_MetaDataDriverFactory {
    constructor();
  }

  export declare class Handle_CDF_MetaDataDriverFactory_2 extends Handle_CDF_MetaDataDriverFactory {
    constructor(thePtr: CDF_MetaDataDriverFactory);
  }

  export declare class Handle_CDF_MetaDataDriverFactory_3 extends Handle_CDF_MetaDataDriverFactory {
    constructor(theHandle: Handle_CDF_MetaDataDriverFactory);
  }

  export declare class Handle_CDF_MetaDataDriverFactory_4 extends Handle_CDF_MetaDataDriverFactory {
    constructor(theHandle: Handle_CDF_MetaDataDriverFactory);
  }

export declare class Handle_CDF_StoreList {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDF_StoreList): void;
  get(): CDF_StoreList;
  delete(): void;
}

  export declare class Handle_CDF_StoreList_1 extends Handle_CDF_StoreList {
    constructor();
  }

  export declare class Handle_CDF_StoreList_2 extends Handle_CDF_StoreList {
    constructor(thePtr: CDF_StoreList);
  }

  export declare class Handle_CDF_StoreList_3 extends Handle_CDF_StoreList {
    constructor(theHandle: Handle_CDF_StoreList);
  }

  export declare class Handle_CDF_StoreList_4 extends Handle_CDF_StoreList {
    constructor(theHandle: Handle_CDF_StoreList);
  }

export declare class Handle_CDM_MetaData {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: CDM_MetaData): void;
  get(): CDM_MetaData;
  delete(): void;
}

  export declare class Handle_CDM_MetaData_1 extends Handle_CDM_MetaData {
    constructor();
  }

  export declare class Handle_CDM_MetaData_2 extends Handle_CDM_MetaData {
    constructor(thePtr: CDM_MetaData);
  }

  export declare class Handle_CDM_MetaData_3 extends Handle_CDM_MetaData {
    constructor(theHandle: Handle_CDM_MetaData);
  }

  export declare class Handle_CDM_MetaData_4 extends Handle_CDM_MetaData {
    constructor(theHandle: Handle_CDM_MetaData);
  }

export declare class Handle_LDOM_MemManager {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: LDOM_MemManager): void;
  get(): LDOM_MemManager;
  delete(): void;
}

  export declare class Handle_LDOM_MemManager_1 extends Handle_LDOM_MemManager {
    constructor();
  }

  export declare class Handle_LDOM_MemManager_2 extends Handle_LDOM_MemManager {
    constructor(thePtr: LDOM_MemManager);
  }

  export declare class Handle_LDOM_MemManager_3 extends Handle_LDOM_MemManager {
    constructor(theHandle: Handle_LDOM_MemManager);
  }

  export declare class Handle_LDOM_MemManager_4 extends Handle_LDOM_MemManager {
    constructor(theHandle: Handle_LDOM_MemManager);
  }

export declare class Handle_PCDM_DriverError {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_DriverError): void;
  get(): PCDM_DriverError;
  delete(): void;
}

  export declare class Handle_PCDM_DriverError_1 extends Handle_PCDM_DriverError {
    constructor();
  }

  export declare class Handle_PCDM_DriverError_2 extends Handle_PCDM_DriverError {
    constructor(thePtr: PCDM_DriverError);
  }

  export declare class Handle_PCDM_DriverError_3 extends Handle_PCDM_DriverError {
    constructor(theHandle: Handle_PCDM_DriverError);
  }

  export declare class Handle_PCDM_DriverError_4 extends Handle_PCDM_DriverError {
    constructor(theHandle: Handle_PCDM_DriverError);
  }

export declare class Handle_PCDM_ReadWriter {
  Nullify(): void;
  IsNull(): boolean;
  reset(thePtr: PCDM_ReadWriter): void;
  get(): PCDM_ReadWriter;
  delete(): void;
}

  export declare class Handle_PCDM_ReadWriter_1 extends Handle_PCDM_ReadWriter {
    constructor();
  }

  export declare class Handle_PCDM_ReadWriter_2 extends Handle_PCDM_ReadWriter {
    constructor(thePtr: PCDM_ReadWriter);
  }

  export declare class Handle_PCDM_ReadWriter_3 extends Handle_PCDM_ReadWriter {
    constructor(theHandle: Handle_PCDM_ReadWriter);
  }

  export declare class Handle_PCDM_ReadWriter_4 extends Handle_PCDM_ReadWriter {
    constructor(theHandle: Handle_PCDM_ReadWriter);
  }

export declare type PCDM_ReaderStatus = {
  PCDM_RS_OK: {};
  PCDM_RS_NoDriver: {};
  PCDM_RS_UnknownFileDriver: {};
  PCDM_RS_OpenError: {};
  PCDM_RS_NoVersion: {};
  PCDM_RS_NoSchema: {};
  PCDM_RS_NoDocument: {};
  PCDM_RS_ExtensionFailure: {};
  PCDM_RS_WrongStreamMode: {};
  PCDM_RS_FormatFailure: {};
  PCDM_RS_TypeFailure: {};
  PCDM_RS_TypeNotFoundInSchema: {};
  PCDM_RS_UnrecognizedFileFormat: {};
  PCDM_RS_MakeFailure: {};
  PCDM_RS_PermissionDenied: {};
  PCDM_RS_DriverFailure: {};
  PCDM_RS_AlreadyRetrievedAndModified: {};
  PCDM_RS_AlreadyRetrieved: {};
  PCDM_RS_UnknownDocument: {};
  PCDM_RS_WrongResource: {};
  PCDM_RS_ReaderException: {};
  PCDM_RS_NoModel: {};
  PCDM_RS_UserBreak: {};
}

export declare type CDF_TypeOfActivation = {
  CDF_TOA_New: {};
  CDF_TOA_Modified: {};
  CDF_TOA_Unchanged: {};
}

export declare type CDM_CanCloseStatus = {
  CDM_CCS_OK: {};
  CDM_CCS_NotOpen: {};
  CDM_CCS_UnstoredReferenced: {};
  CDM_CCS_ModifiedReferenced: {};
  CDM_CCS_ReferenceRejection: {};
}

export declare type PCDM_StoreStatus = {
  PCDM_SS_OK: {};
  PCDM_SS_DriverFailure: {};
  PCDM_SS_WriteFailure: {};
  PCDM_SS_Failure: {};
  PCDM_SS_Doc_IsNull: {};
  PCDM_SS_No_Obj: {};
  PCDM_SS_Info_Section_Error: {};
  PCDM_SS_UserBreak: {};
}

export declare type CDF_TryStoreStatus = {
  CDF_TS_OK: {};
  CDF_TS_NoCurrentDocument: {};
  CDF_TS_NoDriver: {};
  CDF_TS_NoSubComponentDriver: {};
}

export declare type CDF_StoreSetNameStatus = {
  CDF_SSNS_OK: {};
  CDF_SSNS_ReplacingAnExistentDocument: {};
  CDF_SSNS_OpenDocument: {};
}

export declare type CDF_SubComponentStatus = {
  CDF_SCS_Consistent: {};
  CDF_SCS_Unconsistent: {};
  CDF_SCS_Stored: {};
  CDF_SCS_Modified: {};
}

export declare type PCDM_TypeOfFileDriver = {
  PCDM_TOFD_File: {};
  PCDM_TOFD_CmpFile: {};
  PCDM_TOFD_XmlFile: {};
  PCDM_TOFD_Unknown: {};
}

export declare type module_TKCDF_wasm = {
  CDF_MetaDataDriver: typeof CDF_MetaDataDriver;
  CDM_Application: typeof CDM_Application;
  CDF_Application: typeof CDF_Application;
  PCDM_Reader: typeof PCDM_Reader;
  PCDM_Reference: typeof PCDM_Reference;
  PCDM_Reference_1: typeof PCDM_Reference_1;
  PCDM_Reference_2: typeof PCDM_Reference_2;
  PCDM_ReferenceIterator: typeof PCDM_ReferenceIterator;
  PCDM_RetrievalDriver: typeof PCDM_RetrievalDriver;
  PCDM_Writer: typeof PCDM_Writer;
  PCDM_Document: typeof PCDM_Document;
  PCDM_StorageDriver: typeof PCDM_StorageDriver;
  CDM_Reference: typeof CDM_Reference;
  CDM_Document: typeof CDM_Document;
  CDF_Directory: typeof CDF_Directory;
  CDF_FWOSDriver: typeof CDF_FWOSDriver;
  CDF_MetaDataDriverError: typeof CDF_MetaDataDriverError;
  CDF_MetaDataDriverError_1: typeof CDF_MetaDataDriverError_1;
  CDF_MetaDataDriverError_2: typeof CDF_MetaDataDriverError_2;
  CDF_MetaDataDriverFactory: typeof CDF_MetaDataDriverFactory;
  CDF_Store: typeof CDF_Store;
  CDF_StoreList: typeof CDF_StoreList;
  CDM_MetaData: typeof CDM_MetaData;
  CDM_ReferenceIterator: typeof CDM_ReferenceIterator;
  LDOMBasicString: typeof LDOMBasicString;
  LDOMBasicString_1: typeof LDOMBasicString_1;
  LDOMBasicString_2: typeof LDOMBasicString_2;
  LDOMBasicString_3: typeof LDOMBasicString_3;
  LDOMBasicString_4: typeof LDOMBasicString_4;
  LDOMBasicString_5: typeof LDOMBasicString_5;
  LDOMBasicString_6: typeof LDOMBasicString_6;
  LDOMString: typeof LDOMString;
  LDOMString_1: typeof LDOMString_1;
  LDOMString_2: typeof LDOMString_2;
  LDOMString_3: typeof LDOMString_3;
  LDOMString_4: typeof LDOMString_4;
  LDOM_MemManager: typeof LDOM_MemManager;
  LDOM_Node: typeof LDOM_Node;
  LDOM_Node_1: typeof LDOM_Node_1;
  LDOM_Node_2: typeof LDOM_Node_2;
  LDOM_Attr: typeof LDOM_Attr;
  LDOM_Attr_1: typeof LDOM_Attr_1;
  LDOM_Attr_2: typeof LDOM_Attr_2;
  LDOM_NodeList: typeof LDOM_NodeList;
  LDOM_NodeList_1: typeof LDOM_NodeList_1;
  LDOM_NodeList_2: typeof LDOM_NodeList_2;
  LDOM_Element: typeof LDOM_Element;
  LDOM_Element_1: typeof LDOM_Element_1;
  LDOM_Element_2: typeof LDOM_Element_2;
  LDOM_CharacterData: typeof LDOM_CharacterData;
  LDOM_CharacterData_1: typeof LDOM_CharacterData_1;
  LDOM_CharacterData_2: typeof LDOM_CharacterData_2;
  LDOM_Text: typeof LDOM_Text;
  LDOM_Text_1: typeof LDOM_Text_1;
  LDOM_Text_2: typeof LDOM_Text_2;
  LDOM_CDATASection: typeof LDOM_CDATASection;
  LDOM_CDATASection_1: typeof LDOM_CDATASection_1;
  LDOM_CDATASection_2: typeof LDOM_CDATASection_2;
  LDOM_Comment: typeof LDOM_Comment;
  LDOM_Comment_1: typeof LDOM_Comment_1;
  LDOM_Comment_2: typeof LDOM_Comment_2;
  LDOM_Document: typeof LDOM_Document;
  LDOM_Document_1: typeof LDOM_Document_1;
  LDOM_Document_2: typeof LDOM_Document_2;
  LDOM_SBuffer: typeof LDOM_SBuffer;
  LDOM_OSStream: typeof LDOM_OSStream;
  LDOMParser: typeof LDOMParser;
  LDOM_BasicNode: typeof LDOM_BasicNode;
  LDOM_BasicAttribute: typeof LDOM_BasicAttribute;
  LDOM_BasicElement: typeof LDOM_BasicElement;
  LDOM_BasicText: typeof LDOM_BasicText;
  LDOM_CharReference: typeof LDOM_CharReference;
  LDOM_DocumentType: typeof LDOM_DocumentType;
  LDOM_LDOMImplementation: typeof LDOM_LDOMImplementation;
  LDOM_XmlReader: typeof LDOM_XmlReader;
  LDOM_XmlWriter: typeof LDOM_XmlWriter;
  PCDM: typeof PCDM;
  PCDM_DOMHeaderParser: typeof PCDM_DOMHeaderParser;
  PCDM_DriverError: typeof PCDM_DriverError;
  PCDM_DriverError_1: typeof PCDM_DriverError_1;
  PCDM_DriverError_2: typeof PCDM_DriverError_2;
  PCDM_ReadWriter: typeof PCDM_ReadWriter;
  PCDM_ReadWriter_1: typeof PCDM_ReadWriter_1;
  handle: typeof handle;
  Handle_CDF_MetaDataDriver_1: typeof Handle_CDF_MetaDataDriver_1;
  Handle_CDF_MetaDataDriver_2: typeof Handle_CDF_MetaDataDriver_2;
  Handle_CDF_MetaDataDriver_3: typeof Handle_CDF_MetaDataDriver_3;
  Handle_CDF_MetaDataDriver_4: typeof Handle_CDF_MetaDataDriver_4;
  handle: typeof handle;
  Handle_CDM_Application_1: typeof Handle_CDM_Application_1;
  Handle_CDM_Application_2: typeof Handle_CDM_Application_2;
  Handle_CDM_Application_3: typeof Handle_CDM_Application_3;
  Handle_CDM_Application_4: typeof Handle_CDM_Application_4;
  handle: typeof handle;
  Handle_CDF_Application_1: typeof Handle_CDF_Application_1;
  Handle_CDF_Application_2: typeof Handle_CDF_Application_2;
  Handle_CDF_Application_3: typeof Handle_CDF_Application_3;
  Handle_CDF_Application_4: typeof Handle_CDF_Application_4;
  NCollection_Sequence: typeof NCollection_Sequence;
  PCDM_SequenceOfReference_1: typeof PCDM_SequenceOfReference_1;
  PCDM_SequenceOfReference_2: typeof PCDM_SequenceOfReference_2;
  PCDM_SequenceOfReference_3: typeof PCDM_SequenceOfReference_3;
  handle: typeof handle;
  Handle_PCDM_ReferenceIterator_1: typeof Handle_PCDM_ReferenceIterator_1;
  Handle_PCDM_ReferenceIterator_2: typeof Handle_PCDM_ReferenceIterator_2;
  Handle_PCDM_ReferenceIterator_3: typeof Handle_PCDM_ReferenceIterator_3;
  Handle_PCDM_ReferenceIterator_4: typeof Handle_PCDM_ReferenceIterator_4;
  handle: typeof handle;
  Handle_PCDM_RetrievalDriver_1: typeof Handle_PCDM_RetrievalDriver_1;
  Handle_PCDM_RetrievalDriver_2: typeof Handle_PCDM_RetrievalDriver_2;
  Handle_PCDM_RetrievalDriver_3: typeof Handle_PCDM_RetrievalDriver_3;
  Handle_PCDM_RetrievalDriver_4: typeof Handle_PCDM_RetrievalDriver_4;
  handle: typeof handle;
  Handle_PCDM_Writer_1: typeof Handle_PCDM_Writer_1;
  Handle_PCDM_Writer_2: typeof Handle_PCDM_Writer_2;
  Handle_PCDM_Writer_3: typeof Handle_PCDM_Writer_3;
  Handle_PCDM_Writer_4: typeof Handle_PCDM_Writer_4;
  handle: typeof handle;
  Handle_PCDM_Document_1: typeof Handle_PCDM_Document_1;
  Handle_PCDM_Document_2: typeof Handle_PCDM_Document_2;
  Handle_PCDM_Document_3: typeof Handle_PCDM_Document_3;
  Handle_PCDM_Document_4: typeof Handle_PCDM_Document_4;
  handle: typeof handle;
  Handle_PCDM_StorageDriver_1: typeof Handle_PCDM_StorageDriver_1;
  Handle_PCDM_StorageDriver_2: typeof Handle_PCDM_StorageDriver_2;
  Handle_PCDM_StorageDriver_3: typeof Handle_PCDM_StorageDriver_3;
  Handle_PCDM_StorageDriver_4: typeof Handle_PCDM_StorageDriver_4;
  handle: typeof handle;
  Handle_CDM_Reference_1: typeof Handle_CDM_Reference_1;
  Handle_CDM_Reference_2: typeof Handle_CDM_Reference_2;
  Handle_CDM_Reference_3: typeof Handle_CDM_Reference_3;
  Handle_CDM_Reference_4: typeof Handle_CDM_Reference_4;
  handle: typeof handle;
  Handle_CDM_Document_1: typeof Handle_CDM_Document_1;
  Handle_CDM_Document_2: typeof Handle_CDM_Document_2;
  Handle_CDM_Document_3: typeof Handle_CDM_Document_3;
  Handle_CDM_Document_4: typeof Handle_CDM_Document_4;
  handle: typeof handle;
  Handle_CDF_Directory_1: typeof Handle_CDF_Directory_1;
  Handle_CDF_Directory_2: typeof Handle_CDF_Directory_2;
  Handle_CDF_Directory_3: typeof Handle_CDF_Directory_3;
  Handle_CDF_Directory_4: typeof Handle_CDF_Directory_4;
  handle: typeof handle;
  Handle_CDF_FWOSDriver_1: typeof Handle_CDF_FWOSDriver_1;
  Handle_CDF_FWOSDriver_2: typeof Handle_CDF_FWOSDriver_2;
  Handle_CDF_FWOSDriver_3: typeof Handle_CDF_FWOSDriver_3;
  Handle_CDF_FWOSDriver_4: typeof Handle_CDF_FWOSDriver_4;
  handle: typeof handle;
  Handle_CDF_MetaDataDriverError_1: typeof Handle_CDF_MetaDataDriverError_1;
  Handle_CDF_MetaDataDriverError_2: typeof Handle_CDF_MetaDataDriverError_2;
  Handle_CDF_MetaDataDriverError_3: typeof Handle_CDF_MetaDataDriverError_3;
  Handle_CDF_MetaDataDriverError_4: typeof Handle_CDF_MetaDataDriverError_4;
  handle: typeof handle;
  Handle_CDF_MetaDataDriverFactory_1: typeof Handle_CDF_MetaDataDriverFactory_1;
  Handle_CDF_MetaDataDriverFactory_2: typeof Handle_CDF_MetaDataDriverFactory_2;
  Handle_CDF_MetaDataDriverFactory_3: typeof Handle_CDF_MetaDataDriverFactory_3;
  Handle_CDF_MetaDataDriverFactory_4: typeof Handle_CDF_MetaDataDriverFactory_4;
  handle: typeof handle;
  Handle_CDF_StoreList_1: typeof Handle_CDF_StoreList_1;
  Handle_CDF_StoreList_2: typeof Handle_CDF_StoreList_2;
  Handle_CDF_StoreList_3: typeof Handle_CDF_StoreList_3;
  Handle_CDF_StoreList_4: typeof Handle_CDF_StoreList_4;
  handle: typeof handle;
  Handle_CDM_MetaData_1: typeof Handle_CDM_MetaData_1;
  Handle_CDM_MetaData_2: typeof Handle_CDM_MetaData_2;
  Handle_CDM_MetaData_3: typeof Handle_CDM_MetaData_3;
  Handle_CDM_MetaData_4: typeof Handle_CDM_MetaData_4;
  handle: typeof handle;
  Handle_LDOM_MemManager_1: typeof Handle_LDOM_MemManager_1;
  Handle_LDOM_MemManager_2: typeof Handle_LDOM_MemManager_2;
  Handle_LDOM_MemManager_3: typeof Handle_LDOM_MemManager_3;
  Handle_LDOM_MemManager_4: typeof Handle_LDOM_MemManager_4;
  handle: typeof handle;
  Handle_PCDM_DriverError_1: typeof Handle_PCDM_DriverError_1;
  Handle_PCDM_DriverError_2: typeof Handle_PCDM_DriverError_2;
  Handle_PCDM_DriverError_3: typeof Handle_PCDM_DriverError_3;
  Handle_PCDM_DriverError_4: typeof Handle_PCDM_DriverError_4;
  handle: typeof handle;
  Handle_PCDM_ReadWriter_1: typeof Handle_PCDM_ReadWriter_1;
  Handle_PCDM_ReadWriter_2: typeof Handle_PCDM_ReadWriter_2;
  Handle_PCDM_ReadWriter_3: typeof Handle_PCDM_ReadWriter_3;
  Handle_PCDM_ReadWriter_4: typeof Handle_PCDM_ReadWriter_4;
  PCDM_ReaderStatus: typeof PCDM_ReaderStatus;
  CDF_TypeOfActivation: typeof CDF_TypeOfActivation;
  CDM_CanCloseStatus: typeof CDM_CanCloseStatus;
  PCDM_StoreStatus: typeof PCDM_StoreStatus;
  CDF_TryStoreStatus: typeof CDF_TryStoreStatus;
  CDF_StoreSetNameStatus: typeof CDF_StoreSetNameStatus;
  CDF_SubComponentStatus: typeof CDF_SubComponentStatus;
  PCDM_TypeOfFileDriver: typeof PCDM_TypeOfFileDriver;
};
