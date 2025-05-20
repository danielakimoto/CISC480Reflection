
public class RoomWinner {

	public static void main(String[] args) {
		LotteryCard card1 = new LotteryCard("Card 1");
		LotteryCard card2 = new LotteryCard("Card 2");
		LotteryCard card3 = new LotteryCard("Card 3");
		System.out.println("Winning Card Combination:");
		System.out.println("1-red; 2-green; 3-black");
		System.out.println();
		System.out.println("         Color Number");
		card1.print();
		card2.print();
		card3.print();
	}

}
