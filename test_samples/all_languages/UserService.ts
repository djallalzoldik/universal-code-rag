// TypeScript complex test file
interface User {
    id: number;
    username: string;
    email: string;
    roles: string[];
}

type Result<T> =
    | { success: true; data: T }
    | { success: false; error: string };

class UserRepository<T extends User> {
    private cache: Map<number, T> = new Map();

    async findById(id: number): Promise<Result<T>> {
        const user = this.cache.get(id);
        if (user) {
            return { success: true, data: user };
        }
        return { success: false, error: 'User not found' };
    }

    async findAll(): Promise<Result<T[]>> {
        return { success: true, data: Array.from(this.cache.values()) };
    }
}

// Generics with constraints
function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
    return arr.map(fn);
}

// Decorators
function logged(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = async function (...args: any[]) {
        console.log(`Calling ${propertyKey}`);
        return await original.apply(this, args);
    };
}

class UserService {
    constructor(private repo: UserRepository<User>) { }

    @logged
    async getUser(id: number): Promise<User | null> {
        const result = await this.repo.findById(id);
        return result.success ? result.data : null;
    }
}
