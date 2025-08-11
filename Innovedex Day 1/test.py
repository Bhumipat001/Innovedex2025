from position import pick1, pick2, pick3, pick4

def main():
	while True:
		print("\nSelect position to move:")
		print("1: pick1")
		print("2: pick2")
		print("3: pick3")
		print("4: pick4")
		print("0: Exit")
		choice = input("Enter number (0-4): ")

		if choice == '1':
			pick1()
		elif choice == '2':
			pick2()
		elif choice == '3':
			pick3()
		elif choice == '4':
			pick4()
		elif choice == '0':
			print("Exiting program.")
			break
		else:
			print("Invalid choice. Please enter a number from 0 to 4.")

if __name__ == "__main__":
	main()