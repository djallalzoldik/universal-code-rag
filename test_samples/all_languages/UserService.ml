(* Complex OCaml file with advanced features *)

(* Type definitions *)
type user = {
  id: int;
  username: string;
  email: string;
  roles: string list;
}

type 'a result =
  | Ok of 'a
  | Error of string

(* Module signatures *)
module type REPOSITORY = sig
  type 'a t
  val create : unit -> 'a t
  val find_by_id : int -> user t -> user option
  val find_all : user t -> user list
  val save : user -> user t -> user t
end

(* Module implementation *)
module UserRepository : REPOSITORY = struct
  type 'a t = (int, 'a) Hashtbl.t
  
  let create () = Hashtbl.create 10
  
  let find_by_id id repo =
    try Some (Hashtbl.find repo id)
    with Not_found -> None
  
  let find_all repo =
    Hashtbl.fold (fun _ v acc -> v :: acc) repo []
  
  let save user repo =
    Hashtbl.replace repo user.id user;
    repo
end

(* Pattern matching *)
let validate_user user =
  match user with
  | { username = ""; _ } -> Error "Username cannot be empty"
  | { username; _ } when String.length username < 3 ->
      Error "Username too short"
  | { email; _ } when not (String.contains email '@') ->
      Error "Invalid email"
  | _ -> Ok user

(* Higher-order functions *)
let map_users f repo =
  List.map f (UserRepository.find_all repo)

let filter_users predicate repo =
  List.filter predicate (UserRepository.find_all repo)

(* Recursive functions *)
let rec count_roles user =
  match user.roles with
  | [] -> 0
  | _ :: rest -> 1 + List.length rest

(* Functors (parametric modules) *)
module type COMPARABLE = sig
  type t
  val compare : t -> t -> int
end

module MakeSet(Ord: COMPARABLE) = struct
  type element = Ord.t
  type t = element list
  
  let empty = []
  
  let rec mem x = function
    | [] -> false
    | y :: rest -> Ord.compare x y = 0 || mem x rest
  
  let add x s = if mem x s then s else x :: s
end

(* Applicative style *)
let ( >>= ) m f =
  match m with
  | Ok x -> f x
  | Error e -> Error e

let ( <$> ) f m =
  match m with
  | Ok x -> Ok (f x)
  | Error e -> Error e

(* Example usage *)
let process_user user =
  validate_user user >>= fun valid_user ->
  Ok { valid_user with username = String.uppercase_ascii valid_user.username }

(* Polymorphic variants *)
type color = [ `Red | `Green | `Blue ]

let color_to_string = function
  | `Red -> "red"
  | `Green -> "green"
  | `Blue -> "blue"

(* Objects and classes *)
class user_service repo = object (self)
  val mutable repository = repo
  
  method find_by_id id =
    UserRepository.find_by_id id repository
  
  method save user =
    repository <- UserRepository.save user repository;
    Ok user
  
  method count_all =
    List.length (UserRepository.find_all repository)
end
