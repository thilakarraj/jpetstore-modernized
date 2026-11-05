import type { Category, Item, Order, Product } from "@/types/api";

const petImages: Record<string, string> = {
  FISH: "/images/mock/fish.svg",
  DOGS: "/images/mock/dogs.svg",
  REPTILES: "/images/mock/reptiles.svg",
  CATS: "/images/mock/cats.svg",
  BIRDS: "/images/mock/birds.svg",
};

export const mockCategories: Category[] = [
  {
    category_id: "FISH",
    name: "Fish",
    description: "Freshwater and saltwater aquarium companions.",
  },
  {
    category_id: "DOGS",
    name: "Dogs",
    description: "Premium nutrition and accessories for dogs.",
  },
  {
    category_id: "REPTILES",
    name: "Reptiles",
    description: "Habitat essentials for reptile keepers.",
  },
  {
    category_id: "CATS",
    name: "Cats",
    description: "Curated supplies for discerning felines.",
  },
  {
    category_id: "BIRDS",
    name: "Birds",
    description: "Feed, perches, and enrichment for birds.",
  },
];

export const mockProducts: Product[] = [
  {
    product_id: "FI-SW-01",
    category_id: "FISH",
    name: "Angelfish",
    description: "Graceful freshwater angelfish for planted tanks.",
    image_url: petImages.FISH,
  },
  {
    product_id: "FI-SW-02",
    category_id: "FISH",
    name: "Tiger Shark",
    description: "Bold centerpiece species for large marine systems.",
    image_url: petImages.FISH,
  },
  {
    product_id: "K9-BD-01",
    category_id: "DOGS",
    name: "Bulldog",
    description: "Sturdy companion with a loyal temperament.",
    image_url: petImages.DOGS,
  },
  {
    product_id: "K9-RT-01",
    category_id: "DOGS",
    name: "Golden Retriever",
    description: "Classic family dog — friendly and active.",
    image_url: petImages.DOGS,
  },
  {
    product_id: "RP-SN-01",
    category_id: "REPTILES",
    name: "Rattlesnake",
    description: "Advanced keeper species — handle with expertise.",
    image_url: petImages.REPTILES,
  },
  {
    product_id: "FL-DSH-01",
    category_id: "CATS",
    name: "Manx",
    description: "Playful tailless breed with a spirited personality.",
    image_url: petImages.CATS,
  },
  {
    product_id: "AV-SB-01",
    category_id: "BIRDS",
    name: "Amazon Parrot",
    description: "Intelligent vocal companion for experienced owners.",
    image_url: petImages.BIRDS,
  },
  {
    product_id: "AV-CB-01",
    category_id: "BIRDS",
    name: "Finch",
    description: "Delightful aviary favorite with gentle song.",
    image_url: petImages.BIRDS,
  },
];

export const mockItems: Item[] = [
  {
    item_id: "EST-1",
    product_id: "FI-SW-01",
    list_price: "16.50",
    status: "P",
    attribute1: "Large",
    in_stock: true,
    quantity: 10,
  },
  {
    item_id: "EST-2",
    product_id: "FI-SW-01",
    list_price: "14.50",
    status: "P",
    attribute1: "Small",
    in_stock: true,
    quantity: 5,
  },
  {
    item_id: "EST-3",
    product_id: "FI-SW-02",
    list_price: "125.00",
    status: "P",
    attribute1: "Adult",
    in_stock: true,
    quantity: 3,
  },
  {
    item_id: "EST-4",
    product_id: "K9-BD-01",
    list_price: "899.00",
    status: "P",
    attribute1: "Male",
    in_stock: true,
    quantity: 2,
  },
  {
    item_id: "EST-5",
    product_id: "K9-RT-01",
    list_price: "799.00",
    status: "P",
    attribute1: "Female",
    in_stock: true,
    quantity: 4,
  },
  {
    item_id: "EST-6",
    product_id: "RP-SN-01",
    list_price: "249.00",
    status: "P",
    attribute1: "Juvenile",
    in_stock: false,
    quantity: 0,
  },
  {
    item_id: "EST-7",
    product_id: "FL-DSH-01",
    list_price: "199.00",
    status: "P",
    attribute1: "Kitten",
    in_stock: true,
    quantity: 6,
  },
  {
    item_id: "EST-8",
    product_id: "AV-SB-01",
    list_price: "649.00",
    status: "P",
    attribute1: "Hand-fed",
    in_stock: true,
    quantity: 1,
  },
  {
    item_id: "EST-9",
    product_id: "AV-CB-01",
    list_price: "29.00",
    status: "P",
    attribute1: "Pair",
    in_stock: true,
    quantity: 12,
  },
];

let mockOrderSeq = 1000;
export const mockOrders: Order[] = [];

export function getProductImage(product: Product): string {
  return product.image_url ?? petImages[product.category_id] ?? petImages.FISH;
}

export function getItemsForProduct(productId: string): Item[] {
  return mockItems.filter((i) => i.product_id === productId);
}

export function getProductById(productId: string): Product | undefined {
  return mockProducts.find((p) => p.product_id === productId);
}

export function nextMockOrderId(): number {
  mockOrderSeq += 1;
  return mockOrderSeq;
}
