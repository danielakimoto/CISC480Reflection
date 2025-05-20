import java.util.Random;

public class LotteryCard {
	private  int color; //variable for the color number
	private  int number; //variable for the number between 10-15
	private String cardnum; //variable for the name of the card
	private String colorname; //variable for the color name

	LotteryCard(String newcardnum){ //parameterized constructor. sets variables to default position
		color   = 0;
		number  = 0;
		cardnum = newcardnum;
	}

	public void Card() { //generates random values for the variables
		Random rand = new Random();
		color = rand.nextInt(3)+1;
		switch (color) {   //Takes the number generated and returns the color
			case 1:
				colorname = "Red";
				break;
			case 2:
				colorname = "Green";
				break;
			case 3:
				colorname = "Black";
				break;
		}
		number = rand.nextInt(6)+10;
	}

	public void print() { //prints the values for a single card
		Card();
		if(color == 1) {  //if else statement because red has 2 less characters than green and black... makes it print evenly
			System.out.println(cardnum + ":  " + colorname + "     " + number);
		} else {
			System.out.println(cardnum + ":  " + colorname + "   " + number);
	}
}
}
