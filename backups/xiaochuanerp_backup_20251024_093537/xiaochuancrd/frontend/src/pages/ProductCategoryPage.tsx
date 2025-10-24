import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, ChevronDown, ChevronRight, Folder, FolderOpen } from 'lucide-react';
import { apiClient } from '../services/api/client';
import { ProductCategory, ProductCategoryTreeResponse, CreateProductCategoryRequest, UpdateProductCategoryRequest, ProductCategoryWithChildren } from '../types';

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 生成产品分类编码：PC + 6位大写英文加数字组合
const generateCategoryCode = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const prefix = 'PC';
  let randomPart = '';
  for (let i = 0; i < 6; i++) {
    randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return prefix + randomPart;
};

const ProductCategoryPage: React.FC = () => {
  // 产品分类相关状态
   const [productCategories, setProductCategories] = useState<ProductCategory[]>([]);
   const [categoryTree, setCategoryTree] = useState<ProductCategoryTreeResponse | null>(null);
   const [showCategoryForm, setShowCategoryForm] = useState(false);
   const [editingCategory, setEditingCategory] = useState<ProductCategory | null>(null);
   const [categoryFormData, setCategoryFormData] = useState<CreateProductCategoryRequest>({
     categoryName: '',
     categoryCode: generateCategoryCode(),
     description: '',
     parentUuid: '',
     sortOrder: 0
   });
   const [loading, setLoading] = useState(false);
   const [viewMode, setViewMode] = useState<'table' | 'tree'>('table');
   const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  // 树状显示组件
  const CategoryTreeItem: React.FC<{ category: ProductCategoryWithChildren; level: number }> = ({ category, level }) => {
    const hasChildren = category.children && category.children.length > 0;
    const isExpanded = expandedCategories.has(category.uuid);
    
    const toggleExpand = () => {
      const newExpanded = new Set(expandedCategories);
      if (isExpanded) {
        newExpanded.delete(category.uuid);
      } else {
        newExpanded.add(category.uuid);
      }
      setExpandedCategories(newExpanded);
    };

    return (
      <div className="space-y-1">
        <div 
          className={`flex items-center gap-2 py-2 px-3 hover:bg-gray-50 rounded-md cursor-pointer ${
            level > 0 ? 'ml-' + (level * 4) : ''
          }`}
          style={{ marginLeft: `${level * 1.5}rem` }}
        >
          <button
            onClick={toggleExpand}
            className="flex items-center justify-center w-5 h-5 text-gray-400 hover:text-gray-600"
            disabled={!hasChildren}
          >
            {hasChildren ? (
              isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
            ) : (
              <div className="w-1 h-1 bg-gray-300 rounded-full" />
            )}
          </button>
          
          <div className="flex items-center gap-2 flex-1">
            {isExpanded ? <FolderOpen size={16} className="text-blue-500" /> : <Folder size={16} className="text-blue-400" />}
            <span className="font-medium text-gray-900">{category.categoryName}</span>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{category.categoryCode}</span>
            {category.description && (
              <span className="text-sm text-gray-500 truncate">{category.description}</span>
            )}
          </div>
          
          <div className="flex items-center gap-1">
            <button
              onClick={() => handleEditCategory(category)}
              className="text-blue-600 hover:text-blue-900 p-1 rounded"
              title="编辑分类"
            >
              <Edit size={14} />
            </button>
            <button
              onClick={() => handleDeleteCategory(category.uuid)}
              className="text-red-600 hover:text-red-900 p-1 rounded"
              title="删除分类"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
        
        {hasChildren && isExpanded && (
          <div className="space-y-1">
            {category.children!.map((child) => (
              <CategoryTreeItem key={child.uuid} category={child} level={level + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  // 树状显示组件
   const CategoryTreeView: React.FC = () => {
     if (!categoryTree || !categoryTree.items || categoryTree.items.length === 0) {
       return (
         <div className="p-8 text-center text-gray-500">
           <Folder className="w-12 h-12 text-gray-300 mx-auto mb-2" />
           <p>暂无产品分类数据</p>
         </div>
       );
     }

     return (
       <div className="p-4">
         <div className="space-y-1">
           {categoryTree.items.map((category) => (
             <CategoryTreeItem key={category.uuid} category={category} level={0} />
           ))}
         </div>
       </div>
     );
   };

   // 下拉选项组件（用于父分类选择器）
   const CategoryOption: React.FC<{ category: ProductCategoryWithChildren; level: number }> = ({ category, level }) => {
     const hasChildren = category.children && category.children.length > 0;
     
     return (
       <>
         <option value={category.uuid}>
           {'  '.repeat(level)}{category.categoryName} ({category.categoryCode})
         </option>
         {hasChildren && category.children!.map((child) => (
           <CategoryOption key={child.uuid} category={child} level={level + 1} />
         ))}
       </>
     );
   };

  // 获取产品分类列表
  const fetchProductCategories = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getProductCategories();
      // 确保response存在且有items字段
      if (response && response.items) {
        setProductCategories(response.items);
      } else {
        console.error('API返回数据格式错误:', response);
        setProductCategories([]);
      }
    } catch (error) {
      console.error('获取产品分类列表失败:', error);
      setProductCategories([]);
    } finally {
      setLoading(false);
    }
  };

   // 获取产品分类树
  const fetchCategoryTree = async () => {
    try {
      const response = await apiClient.getProductCategoryTree();
      // 确保response存在
      if (response) {
        setCategoryTree(response);
      } else {
        console.error('API返回数据格式错误:', response);
        setCategoryTree([]);
      }
    } catch (error) {
      console.error('获取产品分类树失败:', error);
      setCategoryTree([]);
    }
  };

  useEffect(() => {
     fetchProductCategories();
     fetchCategoryTree();
   }, []);

  // 处理产品分类表单提交
   const handleCategorySubmit = async (e: React.FormEvent) => {
     e.preventDefault();
     
     try {
       // 处理parentUuid字段：如果为空字符串，转换为undefined
       const submitData = {
         ...categoryFormData,
         parentUuid: categoryFormData.parentUuid === '' ? undefined : categoryFormData.parentUuid
       };
       
       if (editingCategory) {
         // 更新产品分类
         await apiClient.updateProductCategory(editingCategory.uuid, submitData as UpdateProductCategoryRequest);
       } else {
         // 创建新产品分类
         await apiClient.createProductCategory(submitData);
       }
       
       setShowCategoryForm(false);
       setEditingCategory(null);
       setCategoryFormData({
         categoryName: '',
         categoryCode: generateCategoryCode(),
         description: '',
         parentUuid: '',
         sortOrder: 0
       });
       
       fetchProductCategories();
       fetchCategoryTree();
     } catch (error) {
       console.error('保存产品分类失败:', error);
     }
   };



  // 编辑产品分类
   const handleEditCategory = (category: ProductCategory) => {
     setEditingCategory(category);
     setCategoryFormData({
       categoryName: category.categoryName,
       categoryCode: category.categoryCode,
       description: category.description || '',
       parentUuid: category.parentUuid || '',
       sortOrder: category.sortOrder || 0
     });
     setShowCategoryForm(true);
   };

   // 删除产品分类
   const handleDeleteCategory = async (uuid: string) => {
     if (window.confirm('确定要删除这个产品分类吗？删除后关联的产品型号将失去分类信息。')) {
       try {
         await apiClient.deleteProductCategory(uuid);
         fetchProductCategories();
         fetchCategoryTree();
       } catch (error) {
         console.error('删除产品分类失败:', error);
       }
     }
   };



   // 重置产品分类表单
   const resetCategoryForm = () => {
     setShowCategoryForm(false);
     setEditingCategory(null);
     setCategoryFormData({
       categoryName: '',
       categoryCode: '',
       description: '',
       parentUuid: '',
       sortOrder: 0
     });
   };



  return (
     <div className="min-h-screen bg-gray-50 p-6">
       <div className="max-w-7xl mx-auto">
         {/* 页面标题和操作按钮 */}
         <div className="mb-6">
           <div className="flex justify-between items-center">
             <h1 className="text-2xl font-bold text-gray-900">产品分类管理</h1>
             <div className="flex items-center gap-4">
               {/* 视图切换按钮 */}
               <div className="flex bg-gray-100 rounded-lg p-1">
                 <button
                   onClick={() => setViewMode('table')}
                   className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                     viewMode === 'table' 
                       ? 'bg-white text-blue-600 shadow-sm' 
                       : 'text-gray-600 hover:text-gray-900'
                   }`}
                 >
                   表格视图
                 </button>
                 <button
                   onClick={() => setViewMode('tree')}
                   className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                     viewMode === 'tree' 
                       ? 'bg-white text-blue-600 shadow-sm' 
                       : 'text-gray-600 hover:text-gray-900'
                   }`}
                 >
                   树状视图
                 </button>
               </div>
               
               <button
                 onClick={() => setShowCategoryForm(true)}
                 className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
               >
                 <Plus size={20} />
                 新增分类
               </button>
             </div>
           </div>
           <p className="text-gray-600 mt-2">管理产品分类信息，支持表格和树状两种视图模式</p>
         </div>

        {/* 内容区域 */}
         <div className="bg-white rounded-lg shadow-sm overflow-hidden">
           {loading ? (
             <div className="p-8 text-center">
               <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
               <p className="mt-2 text-gray-600">加载中...</p>
             </div>
           ) : viewMode === 'table' ? (
             <div className="overflow-x-auto">
               <table className="w-full">
                 <thead className="bg-gray-50">
                   <tr>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类编码</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类名称</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">描述</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">父分类</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">排序</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                     <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                   </tr>
                 </thead>
                 <tbody className="bg-white divide-y divide-gray-200">
                   {productCategories.map((category) => (
                     <tr key={category.uuid} className="hover:bg-gray-50">
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="text-sm font-medium text-gray-900">{category.categoryCode}</div>
                       </td>
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="text-sm font-medium text-gray-900">{category.categoryName}</div>
                       </td>
                       <td className="px-6 py-4">
                         <div className="text-sm text-gray-500 max-w-xs truncate">{category.description || '-'}</div>
                       </td>
                       <td className="px-6 py-4 whitespace-nowrap">
                         <span className="text-sm text-gray-500">
                           {category.parentUuid ? '有父分类' : '根分类'}
                         </span>
                       </td>
                       <td className="px-6 py-4 whitespace-nowrap">
                         <span className="text-sm text-gray-500">{category.sortOrder || 0}</span>
                       </td>
                       <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                         {new Date(category.createdAt).toLocaleDateString('zh-CN')}
                       </td>
                       <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                         <div className="flex gap-2">
                           <button
                             onClick={() => handleEditCategory(category)}
                             className="text-blue-600 hover:text-blue-900"
                           >
                             <Edit size={16} />
                           </button>
                           <button
                             onClick={() => handleDeleteCategory(category.uuid)}
                             className="text-red-600 hover:text-red-900"
                           >
                             <Trash2 size={16} />
                           </button>
                         </div>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
               
               {productCategories.length === 0 && !loading && (
                 <div className="p-8 text-center">
                   <p className="text-gray-500">暂无产品分类数据</p>
                 </div>
               )}
             </div>
           ) : (
             <CategoryTreeView />
           )}
         </div>

        {/* 产品分类表单模态框 */}
        {(showCategoryForm || editingCategory) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-medium text-gray-900">
                  {editingCategory ? '编辑产品分类' : '新增产品分类'}
                </h3>
              </div>
              
              <form onSubmit={handleCategorySubmit} className="p-6 space-y-4">
                <div>
                  <label htmlFor="categoryCode" className="block text-sm font-medium text-gray-700 mb-1">
                    分类编码
                  </label>
                  <input
                    type="text"
                    id="categoryCode"
                    value={categoryFormData.categoryCode}
                    onChange={(e) => setCategoryFormData({ ...categoryFormData, categoryCode: e.target.value })}
                    readOnly={!editingCategory}
                    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      !editingCategory ? 'bg-gray-100 cursor-not-allowed' : ''
                    }`}
                    required
                  />
                  {!editingCategory && (
                    <p className="text-xs text-gray-500 mt-1">系统自动生成的唯一编码</p>
                  )}
                </div>
                
                <div>
                  <label htmlFor="categoryName" className="block text-sm font-medium text-gray-700 mb-1">
                    分类名称
                  </label>
                  <input
                    type="text"
                    id="categoryName"
                    value={categoryFormData.categoryName}
                    onChange={(e) => setCategoryFormData({ ...categoryFormData, categoryName: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="parentUuid" className="block text-sm font-medium text-gray-700 mb-1">
                    父分类
                  </label>
                  <select
                    id="parentUuid"
                    value={categoryFormData.parentUuid || ''}
                    onChange={(e) => setCategoryFormData({ 
                      ...categoryFormData, 
                      parentUuid: e.target.value || null 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">无父分类（根分类）</option>
                    {categoryTree && categoryTree.items && categoryTree.items.map((category) => (
                      <CategoryOption key={category.uuid} category={category} level={0} />
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    选择父分类后，当前分类将作为子分类显示在树状结构中
                  </p>
                </div>
                
                <div>
                  <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-700 mb-1">
                    排序
                  </label>
                  <input
                    type="number"
                    id="sortOrder"
                    value={categoryFormData.sortOrder || 0}
                    onChange={(e) => setCategoryFormData({ 
                      ...categoryFormData, 
                      sortOrder: parseInt(e.target.value) || 0 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    描述
                  </label>
                  <textarea
                    id="description"
                    value={categoryFormData.description || ''}
                    onChange={(e) => setCategoryFormData({ ...categoryFormData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={resetCategoryForm}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {editingCategory ? '更新' : '创建'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        

      </div>
    </div>
  );
};

export default ProductCategoryPage;