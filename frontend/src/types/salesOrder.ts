export interface SalesOrder {
  uuid: string;
  orderNumber: string;
  customerUuid: string;
  customerName: string;
  totalAmount: number;
  status: 'pending' | 'approved' | 'shipped' | 'completed' | 'cancelled';
  orderDate: string;
  deliveryDate?: string;
  shippingAddress?: string;
  notes?: string;
  items?: SalesOrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface SalesOrderItem {
  uuid: string;
  salesOrderUuid: string;
  productUuid: string;
  productName: string;
  productCode: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateSalesOrderRequest {
  customerUuid: string;
  orderDate: string;
  deliveryDate?: string;
  shippingAddress?: string;
  notes?: string;
  items: CreateSalesOrderItemRequest[];
}

export interface CreateSalesOrderItemRequest {
  productUuid: string;
  quantity: number;
  unitPrice: number;
}

export interface UpdateSalesOrderRequest {
  customerUuid?: string;
  orderDate?: string;
  deliveryDate?: string;
  shippingAddress?: string;
  notes?: string;
  status?: 'pending' | 'approved' | 'shipped' | 'completed' | 'cancelled';
}

export interface SalesOrderListParams {
  page?: number;
  size?: number;
  search?: string;
  status?: string;
  customerUuid?: string;
  startDate?: string;
  endDate?: string;
}