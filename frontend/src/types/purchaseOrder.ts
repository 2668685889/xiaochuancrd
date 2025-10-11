export interface PurchaseOrder {
  uuid: string;
  orderNumber: string;
  supplierUuid: string;
  supplierName: string;
  supplierCode?: string;
  totalAmount: number;
  status: 'pending' | 'approved' | 'received' | 'completed' | 'cancelled';
  orderDate: string;
  expectedDate?: string;
  receivedDate?: string;
  notes?: string;
  remark?: string;
  items?: PurchaseOrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface PurchaseOrderItem {
  uuid: string;
  purchaseOrderUuid: string;
  productUuid: string;
  productName: string;
  productCode: string;
  modelUuid?: string;
  modelName?: string;
  selectedSpecification?: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreatePurchaseOrderRequest {
  supplierUuid: string;
  orderDate: string;
  expectedDate?: string;
  notes?: string;
  items: CreatePurchaseOrderItemRequest[];
}

export interface CreatePurchaseOrderItemRequest {
  productUuid: string;
  modelUuid?: string;
  selectedSpecification?: string;
  quantity: number;
  unitPrice: number;
}

export interface UpdatePurchaseOrderRequest {
  supplierUuid?: string;
  orderDate?: string;
  expectedDate?: string;
  notes?: string;
  status?: 'pending' | 'approved' | 'received' | 'completed' | 'cancelled';
}

export interface PurchaseOrderListParams {
  page?: number;
  size?: number;
  search?: string;
  status?: string;
  supplierUuid?: string;
  startDate?: string;
  endDate?: string;
}